import unittest
from ion.eloop import ELoop

class TestELoop(unittest.TestCase):
    def test_init(self):
        ELoop.current().clear()
        e = ELoop()
        with self.assertRaises(RuntimeError):
            ELoop()
        self.assertIsNotNone(ELoop.current(False))

    def test_current(self):
        self.assertIsNotNone(ELoop.current())
        with self.assertRaises(RuntimeError):
            ELoop.current().close()

    def test_instance(self):
        self.assertIsNotNone(ELoop.instance())

    def test_close(self):
        with self.assertRaises(RuntimeError):
            ELoop.current().close()

    def test_clear(self):
        ELoop.current()
        ELoop.current().clear()
        self.assertIsNone(ELoop.current(False))