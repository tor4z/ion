import socket

class TCPClient:
    def __init__(self, family, type):
        self._family = family or socket.AF_INET
        self._type = type or socket.SOCK_STREAM
        self._proto = socket.IPPROTO_TCP
        self._port = None
        self._addr = None
        self._sock = None
        self._closed = False

    def connect(self, addr, port):
        self._addr = addr
        self._port = port
        self._sock = conn_socket(self._family, self._addr, self._type, 
                                self._proto, self._port, 0)

    def send(self, *args, **kwargs):
        if not isinstance(data, bytes):
            raise TypeError("Byte required.")
        self._sock.send(*args, **kwargs)
        
    def recv(self, *args, **kwargs):
        return self._sock.recv(*args, **kwargs)

    def close(self):
        if self._closed:
            raise RuntimeError("TCP client already closed.")
        self._sock.close()
        self._closed = True

def conn_socket(family, addr, type, proto, port, flags):
    sock = None
    for item in set(socket.getaddrinfo(addr, port, family, type, proto, flags)):
        family, type, proto, canonname, sockaddr = item
        try:
            sock = socket.socket(family, type, proto)
        except OSError as e:
            sock = None
            continue
        try:
            sock.connect(sockaddr)
        except OSError as e:
            sock.close()
            sock = None
            continue
        break
    if sock is None:
        raise TCPClientError("Could not connect to {0}:{1}.".format(addr, port))

class TCPClientError(Exception):
    pass