import unittest
import asyncio
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

    def test_instance(self):
        self.assertIsNotNone(ELoop.instance())

    def test_clear(self):
        ELoop.current().clear()
        self.assertIsNone(ELoop.current(False))

    def test_current(self):
        loop = asyncio.get_event_loop()
        eloop = ELoop.current()
        self.assertEqual(loop, eloop._async_loop)