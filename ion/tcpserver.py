import socket
import asyncio
from .iostream import TCPStream

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
        self._loop = asyncio.get_event_loop()
        self._stream_handler = None

    def bind(self, port):
        socks = bind_socket(self._family, None, self._type, 
                               self._proto, port, 0, self._backlog)
        for item in socks:
            fd, sock = item
            self._sockets[fd] = sock

    def start(self):
        for fd, conn in self._sockets.items():
            self._loop.add_reader(fd, self._conn_handler, conn)
            self._started = True

    @property
    def sockets_count(self):
        return len(self._sockets)
    
    def close(self):
        for sock in self._sockets.values():
            sock.close()

    def _conn_handler(self, sock):
        conn, addr = sock.accept()
        stream = TCPStream(conn, addr)
        stream.connect()
        self._handle_stream(stream, addr)

    def stream_handler(self, handler):
        self._stream_handler = handler

    def _handle_stream(self, stream, addr):
        if self._stream_handler is not None:
            self._stream_handler(stream, addr)

def bind_socket(family, addr, type, proto, port, flags, backlog):
    socks = []
    for item in set(socket.getaddrinfo(addr, port, family, type, proto, flags)):
        family, type, proto, canonname, sockaddr = item
        try:
            sock = socket.socket(family, type, proto)
        except OSError as e:
            continue
        try:
            sock.setblocking(False)
            sock.bind(sockaddr)
            sock.listen(backlog)
        except OSError as e:
            sock.close()
            continue
        socks.append((sock.fileno(), sock))
    return socks

