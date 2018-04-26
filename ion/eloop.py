import asyncio
import threading

class ELoop:
    _INSTANCE_NAME = "instance"
    _CURRENT = threading.local()

    def __init__(self, loop=None):
        if hasattr(self._CURRENT, self._INSTANCE_NAME):
            raise RuntimeError("ELoop instance exist.")
        self._async_loop = loop or asyncio.new_event_loop()
        self._CURRENT.instance = self

    @classmethod
    def current(cls, instance=True):
        current = getattr(cls._CURRENT, cls._INSTANCE_NAME, None)
        if current:
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
        try:
            old_loop = asyncio.get_event_loop()
        except RuntimeError:
            old_loop = None
        try:
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_forever()
        finally:
            asyncio.set_event_loop(old_loop)

    def close(self):
        self._async_loop.close()
        del self._CURRENT.instance

    def add_reader(self):
        pass

    def add_writer(self):
        pass

    def add_handler(self):
        pass