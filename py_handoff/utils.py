import socket
import struct
from multiprocessing.connection import Connection, answer_challenge, deliver_challenge
from typing import Tuple, Union


def ClientWithTimeout(
    address: Union[str, Tuple[str, int]], authkey: bytes, timeout: int, use_tcp: bool
) -> Connection:
    """支持超时的 socket 客户端

    Args:
        address (Union[str, Tuple[str, int]]): 如果使用TCP，则是Tuple[str, int]； 如果是unix domain socket, 则是str
        authkey (bytes): [description]
        timeout (int): [description]
        use_tcp (bool): [description]

    Returns:
        (Connection): [description]
    """
    with socket.socket(socket.AF_UNIX if not use_tcp else socket.AF_INET) as s:
        s.setblocking(True)
        s.connect(address)

        # We'd like to call s.settimeout(timeout) here, but that won't work.

        # Instead, prepare a C "struct timeval" to specify timeout. Note that
        # these field sizes may differ by platform.
        seconds = int(timeout)
        microseconds = int((timeout - seconds) * 1e6)
        timeval = struct.pack("@LL", seconds, microseconds)

        # And then set the SO_RCVTIMEO (receive timeout) option with this.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

        # Now create the connection as normal.
        c = Connection(s.detach())

    # The following code will now fail if a socket timeout occurs.

    answer_challenge(c, authkey)
    deliver_challenge(c, authkey)

    return c
