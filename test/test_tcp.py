import unittest
from ion.tcpserver import TCPServer
from ion.tcpclient import TCPClient
from ion.eloop import ELoop

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
        with self.assertRaises(OSError):
            ELoop.current().start()

class TestTCPClient(unittest.TestCase):
    def test_send_recv(self):
        client = TCPClient()
        stream = client.connect("python.org", 80)
        stream.write(b"data")
        data = stream.read(1024).result()
        self.assertTrue("HTTP" in str(data))
        stream.close()

class TestTCP(unittest.TestCase):
    def test_server(self):
        pass