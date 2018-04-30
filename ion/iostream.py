import collections
import asyncio
from asyncio.futures import Future

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
    """
    Methods:
        connect:
        close:
        create_future:

        write:
        read:
        read_until_close:
        read_until:

        _write_handler: not async
        _read_handler: not async

        _write_to_fd:
        _read_from_fd:
    """

    def __init__(self, connctor, loop=None):
        self._read_buffer = bytearray()
        self._write_buffer = Buffer()
        self._connected = False
        self.closed = False
        self._connctor = connctor
        self._fd = connctor.fileno()
        self._loop = loop or asyncio.get_event_loop()
        self._read_fn = None
        self._write_fn = None
        
    def create_future(self):
        return self._loop.create_future()

    def connect(self):
        raise NotImplementedError

    def read(self, size, callback=None):
        data = self._read_form_buffer(size)
        if callback is not None:
            self._run_callback(callback, data)
        return data

    def read_until(self, delimiter, callback=None):
        buffer = self._read_buffer
        if not isinstance(delimiter, bytearray):
            delimiter = bytearray(delimiter)
        pos = buffer.find(delimiter)
        data = self._read_form_buffer(pos)

        if callback is not None:
            self._run_callback(callback, data)
        return data

    async def read_until_close(self, callback=None):
        try:
            fut = self.create_future()
            self._read_from_fd(fut, self._fd)
        except ConnectionResetError as e:
            fut.set_exception(e)
        await fut
        data = self._read_all_form_buffer()
        if callback is not None:
            self._run_callback(callback, data)
        return data

    def _read_all_form_buffer(self):
        return self._read_form_buffer(0)

    def _read_form_buffer(self, size=0):
        b_size = len(self._read_buffer)
        if size >= b_size or size is 0:
            data = self._read_buffer
            self._read_buffer = bytearray()
        else:
            data = self._read_buffer[:size]
            self._read_buffer = self._read_buffer[size:]
        return data

    async def write(self, data):
        self._write_buffer.append(data)
        fut = self.create_future()
        if self._connected:
            self._write_to_fd(fut)
        await fut

    def empty(self):
        return len(self._read_buffer) == 0

    def on_read(self, fn):
        self._read_fn  = fn

    def on_write(self, fn):
        self._write_fn  = fn

    def _read_from_fd(self):
        raise NotImplementedError

    def _write_to_fd(self, fut):
        raise NotImplementedError()

    def _after_connected(self):
        fut = self.create_future()
        self._write_to_fd(fut, None)

    def _before_close(self):
        write_fut = self.create_future()
        self._write_to_fd(write_fut)
        read_fut = self.create_future()
        self._read_from_fd(read_fut, self._fd)

    def _run_callback(self, callback, *args):
        callback(*args)

    async def _handle_write(self):
        fut = self.create_future()
        self._write_to_fd(fut, None)
        if self._write_fn is not None:
            self._write_fn(self)
        await fut

    async def _handle_read(self):
        fut = self.create_future()
        self._read_from_fd(fut, None)
        if self._read_fn is not None and not self.empty():
            self._read_fn(self)
        await fut

class TCPStream(IOStream):

    def __init__(self, connctor, addr, loop=None):
        self._addr = addr
        super().__init__(connctor, loop)

    def connect(self):
        self._loop.add_reader(self._fd, self._handle_read)
        self._loop.add_writer(self._fd, self._handle_write)
        self._connected = True
        self._after_connected()

    def close(self):
        self._before_close()
        self._loop.remove_reader(self._fd)
        self._loop.remove_writer(self._fd)
        self._connctor.close()
        self.closed = True

    def _write_to_fd(self, fut, fd, *args, **kwargs):
        if fd is not None:
            self._loop.remove_writer(fd)

        if fut.cancelled():
            return
        try:
            self.__write_to_fd(*args, **kwargs)
        except (BlockingIOError, InterruptedError):
            self._loop.add_writer(self._fd, self._write_to_fd, fut, 
                self._fd, *args, **kwargs)
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(None)

    def _read_from_fd(self, fut, fd, *args, **kwargs):
        if fd is not None:
            self._loop.remove_reader(fd)

        if fut.cancelled():
            return
        try:
            data = self.__read_from_fd(*args, **kwargs)
        except (BlockingIOError, InterruptedError):
            self._loop.add_reader(self._fd, self._read_from_fd, fut, 
                self._fd ,*args, **kwargs)
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(data)

    def __write_to_fd(self, *args, **kwargs):
        size = len(self._write_buffer)
        if size > 0:
            data = self._write_buffer.peek(size)
            print("write data:", data)
            self._connctor.send(data, *args, **kwargs)

    def __read_from_fd(self, *args, **kwargs):
        size = 1024
        while True:
            data = self._connctor.recv(size, *args, **kwargs)
            if not data: break
            print("read data:", data)
            self._read_buffer += data

class StreamHandler:

    def __init__(self, stream):
        self._stream = stream
        self.setup()
        try:
            self._stream.on_read(self.read)
            self._stream.on_write(self.write)
        finally:
            self.finish()
            if not self._stream.closed:
                self._stream.close()

    def setup(self):
        pass

    def read(self, stream):
        raise NotImplementedError

    def write(self, stream):
        raise NotImplementedError

    def finish(self):
        pass