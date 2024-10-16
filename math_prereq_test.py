import unittest

from math_prereq import (
    ModInt,
    Pol,
)


class ModIntTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(ModInt(5, 17), ModInt(5, 17))
        self.assertEqual(ModInt(22, 17), ModInt(5, 17))
        self.assertEqual(ModInt(-12, 17), ModInt(5, 17))

        self.assertNotEqual(ModInt(5, 17), ModInt(4, 17))
        self.assertNotEqual(ModInt(5, 17), ModInt(5, 16))

    def test_add(self):
        self.assertEqual(ModInt(9, 17) + ModInt(15, 17), ModInt(7, 17))

    def test_sub(self):
        self.assertEqual(ModInt(9, 17) - ModInt(15, 17), ModInt(11, 17))

    def test_mul(self):
        self.assertEqual(ModInt(9, 17) * ModInt(15, 17), ModInt(16, 17))


class PolTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(
            Pol(7, [1, 2, 3]), Pol(7, [ModInt(1, 7), ModInt(2, 7), ModInt(3, 7)])
        )

        self.assertEqual(Pol(7, [1, 2, 3]), Pol(7, [8, -5, 3]))
        self.assertEqual(Pol(7, [1, 2, 3]), Pol(7, [1, 2, 3, 0, 0]))

        self.assertEqual(Pol(7, [0]), Pol(7, []))

        self.assertNotEqual(Pol(7, [1, 2, 3]), Pol(7, [1, 2, 4]))
        self.assertNotEqual(Pol(7, [1, 2, 3]), Pol(7, [1, 2]))

    def test_add(self):
        # Example from slide 24
        f = Pol(7, [5, 0, 4, 3])
        g = Pol(7, [6, 3, 2])
        s = Pol(7, [4, 3, 6, 3])
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 24
        f = Pol(7, [5, 0, 4, 3])
        g = Pol(7, [6, 3, 2])
        d = Pol(7, [6, 4, 2, 3])
        self.assertEqual(f - g, d)

    def test_mul(self):
        # Example from slide 24
        f = Pol(7, [5, 0, 4, 3])
        g = Pol(7, [6, 3, 2])
        p = Pol(7, [2, 1, 6, 2, 3, 6])
        self.assertEqual(f * g, p)
        self.assertEqual(g * f, p)

    def test_mod(self):
        # Example from slide 26
        h = Pol(41, [24, 19, 16, 24, 26, 25, 22])
        m = Pol(41, [1, 0, 0, 0, 1])
        r = Pol(41, [39, 35, 35, 24])
        self.assertEqual(h % m, r)
