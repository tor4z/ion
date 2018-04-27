import socket
from .eloop import ELoop
from .iostream import TCPStream

class TCPClient:
    """
    Basic Example:
    tcp = TCPClient()
    stream = tcp.connect("python.org", 80)
    stream.write("some data")
    print(stream.read(1024))
    stream.close()
    """
    def __init__(self, family=None, type=None):
        self._family = family or socket.AF_INET
        self._type = type or socket.SOCK_STREAM
        self._proto = socket.IPPROTO_TCP

    def connect(self, addr, port):
        sock, sockaddr = self.get_socket(addr, port)
        return self._new_stream(sock, sockaddr)

    def _new_stream(self, sock, sockaddr):
        stream = TCPStream(sock, sockaddr)
        stream.connect()
        return stream

    def get_socket(self, addr, port):
        sockaddr = None
        for item in set(socket.getaddrinfo(addr, port, self._family, self._type, self._proto, 0)):
            family, type, proto, canonname, sockaddr = item
            try:
                sock = socket.socket(family, type, proto)
            except OSError as e:
                sock = None
                continue
        if sock is None:
            raise TCPClientError("Could not connect to {0}:{1}.".format(addr, port))
        return sock, sockaddr

class TCPClientError(Exception):
    pass