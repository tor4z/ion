import unittest
import random
import asyncio
from ion.tcpserver import TCPServer
from ion.tcpclient import TCPClient
from ion.eloop import ELoop
from concurrent.futures import ProcessPoolExecutor

class TestTCPServer(unittest.TestCase):
    def test_bind(self):
        s = TCPServer()
        s.bind(9000)
        self.assertGreater(len(s._sockets), 0)
        s.close()

    def test_start(self):
        s = TCPServer()
        s.bind(9000)
        s.start()
        s.close()

    def test_conn_handler(self):
        s = TCPServer()
        s.bind(9000)
        s.start()
        s.close()

class TestTCPClient(unittest.TestCase):
    def test_send_recv(self):
        async def _exec():
            client = TCPClient()
            stream = await client.connect("python.org", 80)
            await stream.write(b"data")
            data = await stream.read_until_close()
            self.assertTrue("HTTP" in str(data))
            await stream.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_exec())

_str = "abcdefghijklmnopqrstuvwxyz0123456789,./][=-)(*&^%$#@!:}{|}"

async def _client(rs):
    client = TCPClient()
    stream = await client.connect("127.0.0.1", 9000)
    await stream.write(rs)
    data = await stream.read_until_close().result()
    print("recv from server", data)
    await stream.close()

def _server(rs):
    def handler(stream, addr):
        stream.write(rs)
        #data = stream.read_until_close().result()
        print("recv from client", data)

    s = TCPServer()
    s.bind(9000)
    s.start()
    s.stream_handler(handler)
    ELoop.current().test(3)

class TestTCP(unittest.TestCase):
    def test_client_server(self):
        #from asyncio import wrap_future, 
        return
        with ProcessPoolExecutor(max_workers=2) as e:
            rs = "".join(random.choices(_str, 
                    k=random.randint(1, 100000))).encode()
            e.submit(_server, rs)
            e.submit(_client, rs)