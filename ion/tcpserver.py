import socket

DEFAULT_BACKLOG = 128

class TCPServer:
    """
    Basic Example:
    s = TCPServer():
    s.bind(9000)
    s.start()
    ELoop().current().start()
    """
    def __init__(self, family=None, type=None, backlog):
        self._family = family or socket.AF_INET
        self._type = type or socket.SOCK_STREAM
        self._proto = socket.IPPROTO_TCP
        self._sockets = {}
        self._backlog = backlog or DEFAULT_BACKLOG
        self._satrted = False

    def bind(self, port):
        socks = bind_socket(self._family, None, self._type, 
                               self._proto, port, None, self._backlog)
        for s in socks:
            fd, sock = s
            self._sockets[fd] = s

    def start(self):
        pass

    @property
    def sockets_count(self):
        return len(self._sockets)
    
    def close(self):
        for cosk in self._sockets.value():
            sock.close()

    def _handler_conn(self, conn):
        pass

def bind_socket(family, addr, type, proto, port, flags, backlog):
    socks = []
    for item in set(socket.getaddrinfo(addr, port, family, type, proto, flags)):
        family, type, proto, canonname, sockaddr = item
        try:
            sock = socket(family, type, proto)
        except OSError as e:
            continue
        try:
            sock.bind(sockaddr)
            sock.listen(backlog)
        except OSError as e:
            sock.close()
            continue
        socks.append((sock.fileno(), sock))
    return socks


def add_accept_handler(fd, func):
    pass