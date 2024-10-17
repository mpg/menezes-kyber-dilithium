import unittest

from math_prereq import (
    Mod,
    Pol,
)


class ModIntTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(Mod(5, 17), Mod(5, 17))
        self.assertEqual(Mod(22, 17), Mod(5, 17))
        self.assertEqual(Mod(-12, 17), Mod(5, 17))

        self.assertNotEqual(Mod(5, 17), Mod(4, 17))
        self.assertNotEqual(Mod(5, 17), Mod(5, 16))

    def test_add(self):
        self.assertEqual(Mod(9, 17) + Mod(15, 17), Mod(7, 17))

    def test_sub(self):
        self.assertEqual(Mod(9, 17) - Mod(15, 17), Mod(11, 17))

    def test_mul(self):
        self.assertEqual(Mod(9, 17) * Mod(15, 17), Mod(16, 17))


class PolTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(Pol(7, [1, 2, 3]), Pol(7, [Mod(1, 7), Mod(2, 7), Mod(3, 7)]))

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


class ModPolGenTest(unittest.TestCase):
    def test_equal(self):
        # Example from slide 26
        h = Pol(41, [24, 19, 16, 24, 26, 25, 22])
        m = Pol(41, [1, 0, 0, 0, 1])
        r = Pol(41, [39, 35, 35, 24])
        self.assertEqual(Mod(h, m), Mod(r, m))

        # wrong leading coefficient
        r2 = Pol(41, [39, 35, 35, 25])
        self.assertNotEqual(Mod(h, m), Mod(r2, m))

    def test_add(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = Mod(Pol(41, [32, 0, 17, 22]), m)
        g = Mod(Pol(41, [11, 7, 19, 1]), m)
        # result computed manually
        s = Mod(Pol(41, [2, 7, 36, 23]), m)
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = Mod(Pol(41, [32, 0, 17, 22]), m)
        g = Mod(Pol(41, [11, 7, 19, 1]), m)
        # results computed manually
        d1 = Mod(Pol(41, [21, 34, 39, 21]), m)
        d2 = Mod(Pol(41, [-21, -34, -39, -21]), m)
        self.assertEqual(f - g, d1)
        self.assertEqual(g - f, d2)

    def test_mul(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = Mod(Pol(41, [32, 0, 17, 22]), m)
        g = Mod(Pol(41, [11, 7, 19, 1]), m)
        r = Mod(Pol(41, [39, 35, 35, 24]), m)
        self.assertEqual(f * g, r)
        self.assertEqual(g * f, r)
