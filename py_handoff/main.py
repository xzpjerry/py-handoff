import json
import os
import select
import socket
import threading
import uuid
from multiprocessing.connection import Listener
from socket import error as SocketError
from time import sleep

import netifaces as ni
import pyperclip
from lru import LRU

from py_handoff.utils import ClientWithTimeout

DISCOVERY_PORT = int(os.environ.get("PY_HANDOFF_DISCOVERY_PORT", 5005))
DISCOVERY_KEY = os.environ.get("PY_HANDOFF_KEY", "D0AA67DD-C285-45A2-B7A7-F5277F613E3C")
CLIPBOARD_LISTENER_PORT = int(
    os.environ.get("PY_HANDOFF_CLIPBOARD_LISTENER_PORT", 6000)
)
CLIPBOARD_SIZE_LIMIT_IN_MB = int(
    os.environ.get("PY_HANDOFF_CLIPBOARD_SIZE_LIMIT_IN_MB", 128)
)

self_id = uuid.uuid4().hex
tcp_listener_auth_key = uuid.uuid4().hex
listener = Listener(
    address=("0.0.0.0", CLIPBOARD_LISTENER_PORT), authkey=tcp_listener_auth_key.encode()
)
# Monkey Patch to support select
Listener.fileno = lambda self: self._listener._socket.fileno()

incoming_clip = LRU(5)
connected_nodes_and_retries_map = LRU(32)

# Assume one character takes 4 bytes
clipboard_max_len = CLIPBOARD_SIZE_LIMIT_IN_MB * 1024 * 1024 // 4


def obfuscate_with_discovery_key(byt):
    # Use same function in both directions.  Input and output are bytes
    # objects.
    mask = DISCOVERY_KEY.encode()
    lmask = len(mask)
    return bytes(c ^ mask[i % lmask] for i, c in enumerate(byt))


def encode_broadcast_msg(msg):
    msg = json.dumps(
        {
            "msg": msg,
            "from": self_id,
        }
    )
    msg = msg.encode()
    msg = obfuscate_with_discovery_key(msg)
    return msg


def decode_broadcast_msg(data):
    try:
        data = obfuscate_with_discovery_key(data)
        data = data.decode()
        data = json.loads(data)
        return data["msg"], data["from"]
    except Exception as e:
        print(e)
        return None, None


def waitForNewPaste():
    originalText = pyperclip.paste()[:clipboard_max_len]
    while True:
        currentText = pyperclip.paste()[:clipboard_max_len]
        if currentText != originalText:
            return currentText
        sleep(1)


def transmit_clipboard_changes():
    while True:
        msg = waitForNewPaste()
        if msg in incoming_clip:
            continue
        failed_nodes = []
        for (
            address,
            auth_key,
        ), failure_times in connected_nodes_and_retries_map.items():
            print(
                f"Transmiting clipboard to {(address, auth_key)}, which had failed {failure_times} times"
            )
            try:
                with ClientWithTimeout(
                    address, authkey=auth_key, timeout=3, use_tcp=True
                ) as conn:
                    conn.send(msg)
            except SocketError as e:
                if failure_times >= 3:
                    failed_nodes.append((address, auth_key))
                else:
                    connected_nodes_and_retries_map[(address, auth_key)] += 1

        for node in failed_nodes:
            connected_nodes_and_retries_map.pop(node)


def auto_discovery():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", DISCOVERY_PORT))
    while True:
        data, addr = sock.recvfrom(1500)
        msg, from_id = decode_broadcast_msg(data)
        if msg is not None and from_id != self_id:
            msg = msg.split(",")
            if len(msg) == 2:
                port, auth_key = msg
                try:
                    key = ((addr[0], int(port)), auth_key.encode())
                    print(f"Registering node {key}")
                    connected_nodes_and_retries_map[key] = 0
                except:
                    pass


def broadcast_self():
    self_listener_cfg = f"{CLIPBOARD_LISTENER_PORT},{tcp_listener_auth_key}"
    self_listener_cfg = encode_broadcast_msg(self_listener_cfg)
    while True:
        interfaces = ni.interfaces()
        for interface in interfaces:
            ifaddress = ni.ifaddresses(interface)
            if not ifaddress or 2 not in ifaddress:
                continue
            try:
                ip = ifaddress[2][0]["addr"]
                sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
                )  # UDP
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((ip, 0))
                sock.sendto(self_listener_cfg, ("255.255.255.255", DISCOVERY_PORT))
                sock.close()
            except Exception as e:
                print(
                    f"Exception occurred when broadcasting self on {ip}: {type(e)} - {e};"
                )
            else:
                print(f"Broadcasted self on {ip}")
        sleep(30)


def listen_for_incoming_clip():
    while True:
        r, w, e = select.select((listener,), (), ())
        if listener in r:
            with listener.accept() as conn:
                print("Incoming clipboard")
                clip_board = conn.recv()
                try:
                    incoming_clip[clip_board] = True
                    pyperclip.copy(clip_board)
                except Exception as exc:
                    print(
                        f"Exception occurred when handling incoming clipboard: {type(exc)} - {exc};"
                    )


def entrypoint():
    broadcast_self_thread = threading.Thread(target=broadcast_self)
    broadcast_self_thread.start()

    auto_discovery_thread = threading.Thread(target=auto_discovery)
    auto_discovery_thread.start()

    listen_for_incoming_clip_thread = threading.Thread(target=listen_for_incoming_clip)
    listen_for_incoming_clip_thread.start()

    transmit_clipboard_changes()
