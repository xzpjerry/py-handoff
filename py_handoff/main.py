import json
import socket
import threading
import uuid
import gzip

import pyperclip

PORT = 5005
KEY = "this is a secret key!"

self_id = uuid.uuid4().hex
previous_clipboard = ""


def obfuscate(byt):
    # Use same function in both directions.  Input and output are bytes
    # objects.
    mask = KEY.encode()
    lmask = len(mask)
    return bytes(c ^ mask[i % lmask] for i, c in enumerate(byt))


def encode_msg(msg):
    msg = json.dumps({"msg": msg, "from": self_id,})
    msg = msg.encode()
    msg = gzip.compress(msg, compresslevel=9)
    msg = obfuscate(msg)
    return msg


def decode_msg(data):
    data = obfuscate(data)
    data = gzip.decompress(data)
    data = data.decode()
    data = json.loads(data)
    return data["msg"], data["from"]


def server():
    """Broadcasting clipboard changes to LAN
    """
    while True:
        msg = pyperclip.waitForNewPaste()
        interfaces = socket.getaddrinfo(
            host=socket.gethostname(), port=None, family=socket.AF_INET
        )
        msg = encode_msg(msg)
        for ip in {ip[-1][0] for ip in interfaces}:
            try:
                sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
                )  # UDP
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((ip, 0))

                sock.sendto(msg, ("255.255.255.255", PORT))
                sock.close()
            except Exception as e:
                print(e)


def client():
    """Subscribing clipboard changes from remote, and updating to local
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", PORT))
    while True:
        data = sock.recv(1024)
        msg, from_id = decode_msg(data)
        if from_id != self_id:
            try:
                pyperclip.copy(msg)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    server_thread = threading.Thread(target=server)
    server_thread.start()
    client()
