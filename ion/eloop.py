import asyncio
import threading

def status_checker(func):
    def _exec(*args, **kwargs):
        try:
            obj = args[0]
        except IndexError:
            obj = None
        finally:
            if obj is None or not isinstance(obj, ELoop):
                raise RuntimeError("status_checker ONLY can be used in ELoop.")
        if not obj._started:
            raise RuntimeError("ELoop not started.")
        func(*args, **kwargs)
    return _exec

class ELoop:
    _INSTANCE_NAME = "instance"
    _CURRENT = threading.local()

    def __init__(self, loop=None):
        if hasattr(self._CURRENT, self._INSTANCE_NAME):
            raise RuntimeError("ELoop instance exist.")
        self._started = False
        self._async_loop = loop or asyncio.get_event_loop()
        self._CURRENT.instance = self

    @classmethod
    def current(cls, instance=True):
        current = getattr(cls._CURRENT, cls._INSTANCE_NAME, None)
        if current:
            # print(current._async_loop)
            return current
        else:
            if instance:
                loop = asyncio.get_event_loop()
                current = cls._make_instance(loop)
        return current

    @classmethod
    def instance(cls):
        return cls.current(True)
        
    @classmethod
    def _make_instance(cls, loop):
        instance = cls(loop)
        cls._CURRENT.instance = instance
        return instance

    def start(self):
        if self._started:
            raise RuntimeError("ELoop can not be start twice.")
        try:
            old_loop = asyncio.get_event_loop()
        except RuntimeError:
            old_loop = None
        try:
            self._started = True
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_forever()
        finally:
            asyncio.set_event_loop(old_loop)

    def test(self, timeout):
        self._async_loop.call_later(timeout, self.clear)
        self.start()

    def clear(self):
        try:
            del self._CURRENT.instance
        except AttributeError:
            pass

    def add_reader(self, fd, callback, *args):
        self._async_loop.add_reader(fd, callback, *args)

    def remove_reader(self, fd):
        self._async_loop.remove_reader(fd)

    def add_writer(self, fd, callback, *args):
        self._async_loop.add_writer(fd, callback, *args)

    def remove_writer(self, fd):
        self._async_loop.remove_writer(fd)
