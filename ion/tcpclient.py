import socket
import functools
import asyncio
from .iostream import TCPStream, StreamHandler
from .connector import ABCConnector

class Connector(ABCConnector):

    def __init__(self, sock, addr, loop=None):
        super().__init__(loop)
        self._socket = sock
        self._addr = addr
        self._fileno = sock.fileno()

    async def start(self):
        fut = self.create_future()
        self._connect(fut)
        await fut

    def _connect(self, fut):
        try:
            self._socket.setblocking(False)
            self._socket.connect(self._addr)
        except (BlockingIOError, InterruptedError):
            fut.add_done_callback(self._connect_done)
            self._loop.add_writer(
                self.fileno(), self._connect_done_callback, fut
            )
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(None)

    def _connect_done(self, fut):
        self._loop.remove_writer(self.fileno())

    def _connect_done_callback(self, fut):
        if fut.cancelled():
            return

        try:
            err = self._socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                raise OSError(err, f"Connect to {self._addr} fail.")
        except (BlockingIOError, InterruptedError):
            pass
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(None)

    def close(self):
        self._socket.close()

    def fileno(self):
        return self._fileno

    def send(self, data, *args, **kwargs):
        self._socket.send(data, *args, **kwargs)

    def recv(self, size, *args, **kwargs):
        return self._socket.recv(size, *args, **kwargs)

class TCPClient:
    def __init__(self, family=None, type=None):
        self._family = family or socket.AF_INET
        self._type = type or socket.SOCK_STREAM
        self._proto = socket.IPPROTO_TCP
        self._loop = asyncio.get_event_loop()
        self._handler_cls = None

    async def connect(self, addr, port):
        sock, sockaddr = self.get_socket(addr, port)
        stream = await self._new_stream(sock, sockaddr)
        if self._handler_cls is None:
            return stream
        else:
            self._handler_cls(stream)

    def handle(self, handler):
        self._handler_cls = handler

    async def _new_stream(self, sock, sockaddr):
        connctor = Connector(sock, sockaddr, self._loop)
        await connctor.start()
        stream = TCPStream(connctor, sockaddr)
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

class TCPConnError(Exception):
    pass