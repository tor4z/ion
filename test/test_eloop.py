import unittest
from ion.eloop import ELoop

class TestELoop(unittest.TestCase):
    def test_init(self):
        e = ELoop()
        with self.assertRaises(RuntimeError):
            ELoop()
        self.assertIsNotNone(ELoop.current(False))
        e.close()

    def test_current(self):
        self.assertIsNone(ELoop.current(False))
        self.assertIsNotNone(ELoop.current())
        ELoop.current().close()

    def test_instance(self):
        self.assertIsNotNone(ELoop.instance())
        ELoop.current().close()

    def test_close(self):
        ELoop.instance()
        ELoop.current().close()
        self.assertIsNone(ELoop.current(False))