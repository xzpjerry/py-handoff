import socket
from time import sleep
from tkinter import Tk

PORT = 5005
KEY = "this is a secret key!"
r = Tk()
r.withdraw()
previous_clipboard = ""


def obfuscate(string, key=None):
    key = key or KEY
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string


def clearify(string, key=None):
    key = key or KEY
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string


def set_clipboard(to_str: str):
    r.clipboard_clear()
    r.clipboard_append(to_str)
    r.update()


def blocking_get_clipboard_if_changed():
    global previous_clipboard
    while True:
        tmp = r.clipboard_get()
        if tmp != previous_clipboard:
            previous_clipboard = tmp
            return previous_clipboard
        sleep(1)


def paste():
    """Broadcasting clipboard changes to LAN
    """
    while True:
        msg = blocking_get_clipboard_if_changed()
        interfaces = socket.getaddrinfo(
            host=socket.gethostname(), port=None, family=socket.AF_INET
        )
        allips = {ip[-1][0] for ip in interfaces}
        for ip in allips:
            sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
            )  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind((ip, 0))
            msg = obfuscate(msg)
            sock.sendto(msg.encode(), ("255.255.255.255", PORT))
            sock.close()


def copy():
    """Subscribing clipboard changes from remote, and updating to local
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", PORT))
    while True:
        data = sock.recv(1024).decode()
        set_clipboard(clearify(data))


if __name__ == "__main__":
    import threading

    server_thread = threading.Thread(target=paste)
    client_thread = threading.Thread(target=copy)
    server_thread.start()
    client_thread.start()

    r.mainloop()
