import unittest
from random import choices, randint
from ion.iostream import Buffer

_str = "abcdefghijklmnopqrstuvwxyz0123456789,./][=-)(*&^%$#@!:}{|}"

class TestBuffer(unittest.TestCase):
    def test_append(self):
        for n in range(20):
            buffer = Buffer()
            k = n*512
            rs = "".join(choices(_str, k=k))
            buffer.append(rs.encode())
            self.assertEqual(len(buffer), k)
            buffer.clear()
            del buffer
    
    def count_size(self, bs, ps):
        res = bs - ps
        if res < 0:
            res = 0
        return res

    def test_pop(self):
        for n in range(1, 40):
            buffer = Buffer()
            k = n * randint(1, 512)
            j = n * randint(1, 512)
            rs = "".join(choices(_str, k=k)).encode()
            buffer.append(rs)
            self.assertEqual(len(buffer), k)
            data = buffer.pop(j)
            self.assertEqual(data, rs[:j])
            self.assertEqual(len(buffer), self.count_size(k, j))
            buffer.clear()
            del buffer
