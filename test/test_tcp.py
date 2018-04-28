import unittest
import random
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
        client = TCPClient()
        stream = client.connect("python.org", 80)
        stream.write(b"data")
        data = stream.read(1024).result()
        self.assertTrue("HTTP" in str(data))
        stream.close()

_str = "abcdefghijklmnopqrstuvwxyz0123456789,./][=-)(*&^%$#@!:}{|}"

def _client(rs):
    client = TCPClient()
    stream = client.connect("127.0.0.1", 9000)
    stream.write(rs)
    data = stream.read(1024).result()
    print("recv from server", data)
    stream.close()

def _server(rs):
    s = TCPServer()
    s.bind(9000)
    s.start()
    ELoop.current().test(1)

class TestTCP(unittest.TestCase):
    def test_client_server(self):
        with ProcessPoolExecutor(max_workers=2) as e:
            rs = "".join(random.choices(_str, k=random.randint(1, 100000))).encode()
            e.submit(_server, rs)
            e.submit(_client, rs)