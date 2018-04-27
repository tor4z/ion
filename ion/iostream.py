import collections
from concurrent.futures import Future
from .eloop import ELoop

class Buffer:
    _BIG_DATA = 2048
    def __init__(self):
        self._data = collections.deque()
        self._start = 0
        self._size = 0

    def __len__(self):
        return self.size()

    def size(self):
        return self._size

    def append(self, data):
        size = len(data)
        try:
            last = self._data[-1]
        except:
            last = b""

        last_size = len(last)
        if last_size > 0:
            last = self._data.pop()

        if size + last_size <= self._BIG_DATA:
            last += data
            self._data.append(last)
        elif last_size >= self._BIG_DATA:
            self._data.append(data)
        else:
            remaining = self._BIG_DATA-last_size
            last += data[0:remaining]
            self._data.append(last)
            self._data.append(data[remaining:])
        self._size += size

    def pop(self, size=None):
        if size is None or size >= self.size():
            size = self.size()
        if size <= 0:
            raise ValueError("size should be greater than 0.")

        try:
            b = self._data[0]
            b_size = len(b)
            if b_size < size:
                data = b
                self._data.popleft()
                self._start = 0
                self._size -= b_size
                data += self.pop(size - b_size)
            elif b_size > size:
                data = b[self._start: self._start + size]
                self._start += size
                self._size -= size
            else:
                data = b
                self._data.popleft()
                self._start = 0
                self._size -= size
        except IndexError:
            data = b""
            self._size = 0
        return data

    def peek(self, size):
        return self.pop(size)

    def clear(self):
        self._data.clear()
        self._size = 0

class IOStream:
    def __init__(self):
        self._read_buffer = bytearray()
        self._write_buffer = Buffer()
        self._connected = False

    def connect(self):
        raise NotImplementedError

    def read(self, size, callback=None):
        self._write_to_buffer()
        data = self._read_form_buffer(size)
        return self._return_data(data, callback)

    def read_until(self, delimiter, callback=None):
        buffer = self._read_buffer
        if not isinstance(delimiter, bytearray):
            delimiter = bytearray(delimiter)
        pos = buffer.find(delimiter)
        data = self._read_form_buffer(pos)
        return self._return_data(data, callback)

    def _return_data(self, data, callback):
        if callback is None:
            future = Future()
            future.set_result(data)
        else:
            self._run_callback(callback, data)
            future = None
        return future

    def _read_form_buffer(self, size):
        b_size = len(self._read_buffer)
        if size >= b_size:
            data = self._read_buffer
            self._read_buffer = bytearray()
        else:
            data = self._read_buffer[:size]
            self._read_buffer = self._read_buffer[size:]
        return data

    def write(self, data):
        self._write_buffer.append(data)
        if self._connected:
            self._write_to_fd()

    def _write_to_buffer(self):
        raise NotImplementedError

    def _write_to_fd(self):
        raise NotImplementedError()

    def _after_connected(self):
        self._connected = True
        self._write_to_fd()

    def _before_close(self):
        self._write_to_fd()

    def _run_callback(self, callback, *args):
        callback(*args)

class TCPStream(IOStream):
    def __init__(self, sock, addr):
        self._loop = ELoop.current()
        self._socket = sock
        self._fd = sock.fileno()
        self._addr = addr
        super().__init__()

    def connect(self):
        try:
            self._socket.connect(self._addr)
        except OSError:
            self._socket.close()
            raise TCPConnError()
        
        self._loop.add_reader(self._fd, self._handle_read)
        self._loop.add_writer(self._fd, self._handle_write)
        self._after_connected()

    def close(self):
        self._before_close()
        self._loop.remove_reader(self._fd)
        self._loop.remove_writer(self._fd)
        self._socket.close()

    def _handle_write(self):
        self._write_to_fd()

    def _handle_read(self):
        self._write_to_buffer()
    
    def _write_to_fd(self):
        size = len(self._write_buffer)
        if size > 0:
            data = self._write_buffer.peek(size)
            self._socket.send(data)

    def _write_to_buffer(self):
        size = 1024
        while True:
            data = self._socket.recv(size)
            if not data: break
            self._read_buffer += data


class TCPConnError(Exception):
    pass