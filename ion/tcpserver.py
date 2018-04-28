import socket
from .eloop import ELoop

DEFAULT_BACKLOG = 128

class TCPServer:
    """
    Basic Example:
    s = TCPServer():
    s.bind(9000)
    s.start()
    ELoop().current().start()
    """
    def __init__(self, family=None, type=None, backlog=None):
        self._family = family or socket.AF_INET
        self._type = type or socket.SOCK_STREAM
        self._proto = socket.IPPROTO_TCP
        self._sockets = {}
        self._backlog = backlog or DEFAULT_BACKLOG
        self._started = False

    def bind(self, port):
        socks = bind_socket(self._family, None, self._type, 
                               self._proto, port, 0, self._backlog)
        for item in socks:
            fd, sock = item
            self._sockets[fd] = sock

    def start(self):
        for fd, conn in self._sockets.items():
            add_accept_handler(fd, self._conn_handler, conn)
            self._started = True

    @property
    def sockets_count(self):
        return len(self._sockets)
    
    def close(self):
        for sock in self._sockets.values():
            sock.close()

    def _conn_handler(self, sock):
        conn, addr = sock.accept()
        print("recv from clinet", conn.recv(1024))
        conn.send(b"data")

def bind_socket(family, addr, type, proto, port, flags, backlog):
    socks = []
    for item in set(socket.getaddrinfo(addr, port, family, type, proto, flags)):
        family, type, proto, canonname, sockaddr = item
        try:
            sock = socket.socket(family, type, proto)
        except OSError as e:
            continue
        try:
            sock.setblocking(True)
            sock.bind(sockaddr)
            sock.listen(backlog)
        except OSError as e:
            sock.close()
            continue
        socks.append((sock.fileno(), sock))
    return socks


def add_accept_handler(fd, handler, conn):
    loop = ELoop.current()
    loop.add_reader(fd, handler, conn)