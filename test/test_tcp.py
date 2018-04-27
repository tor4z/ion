import unittest
from ion.tcpserver import TCPServer
from ion.tcpclient import TCPClient

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

class TestTCPClient(unittest.TestCase):
    pass

class TestTCP(unittest.TestCase):
    def test_server(self):
        pass