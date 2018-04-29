import asyncio

class ABCConnector:
    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()

    def create_future(self):
        return self._loop.create_future()

    def start(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
    
    def fileno(self):
        raise NotImplementedError

    def send(self):
        raise NotImplementedError

    def recv(self):
        raise NotImplementedError