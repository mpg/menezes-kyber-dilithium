import unittest

import math

from math_prereq import (
    ModInt,
    Pol,
    ModPolGen,
    ModPol,
    Vec,
    Mat,
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

    def test_size(self):
        self.assertEqual(ModInt(0, 4).size(), 0)
        self.assertEqual(ModInt(1, 4).size(), 1)
        self.assertEqual(ModInt(2, 4).size(), 2)
        self.assertEqual(ModInt(3, 4).size(), 1)

        self.assertEqual(ModInt(0, 5).size(), 0)
        self.assertEqual(ModInt(1, 5).size(), 1)
        self.assertEqual(ModInt(2, 5).size(), 2)
        self.assertEqual(ModInt(3, 5).size(), 2)
        self.assertEqual(ModInt(4, 5).size(), 1)


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

    def test_size(self):
        # Example from slide 33
        f = Pol(19, [1, 12, 0, 3, 0, 18])
        self.assertEqual(f.size(), 7)

        # Example from slide 34
        g = Pol(31, [1, 30, 29, 0, 1, 2])
        self.assertEqual(g.size(), 2)


class ModPolGenTest(unittest.TestCase):
    def test_equal(self):
        # Example from slide 26
        h = Pol(41, [24, 19, 16, 24, 26, 25, 22])
        m = Pol(41, [1, 0, 0, 0, 1])
        r = Pol(41, [39, 35, 35, 24])
        self.assertEqual(ModPolGen(h, m), ModPolGen(r, m))

        # wrong leading coefficient
        r2 = Pol(41, [39, 35, 35, 25])
        self.assertNotEqual(ModPolGen(h, m), ModPolGen(r2, m))

    def test_add(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [32, 0, 17, 22]), m)
        g = ModPolGen(Pol(41, [11, 7, 19, 1]), m)
        # result computed manually
        s = ModPolGen(Pol(41, [2, 7, 36, 23]), m)
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [32, 0, 17, 22]), m)
        g = ModPolGen(Pol(41, [11, 7, 19, 1]), m)
        # results computed manually
        d1 = ModPolGen(Pol(41, [21, 34, 39, 21]), m)
        d2 = ModPolGen(Pol(41, [-21, -34, -39, -21]), m)
        self.assertEqual(f - g, d1)
        self.assertEqual(g - f, d2)

    def test_mul(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [32, 0, 17, 22]), m)
        g = ModPolGen(Pol(41, [11, 7, 19, 1]), m)
        r = ModPolGen(Pol(41, [39, 35, 35, 24]), m)
        self.assertEqual(f * g, r)
        self.assertEqual(g * f, r)

    def test_size(self):
        # Examples from slide 35
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [1, 1, -2, 2]), m)
        g = ModPolGen(Pol(41, [-2, 0, 2, -1]), m)
        self.assertEqual(f.size(), 2)
        self.assertEqual(g.size(), 2)
        self.assertEqual((f * g).size(), 8)


class ModPolTest(unittest.TestCase):
    def test_equal(self):
        r0 = ModPol(41, 4, [39, 35, 35, 24])
        r1 = ModPol(41, 4, [-2, 35, -6, 24])
        self.assertEqual(r0, r1)

        # wrong leading coefficient
        r2 = ModPol(41, 4, [39, 35, 35, 25])
        self.assertNotEqual(r0, r2)

        # wrong integer modulus
        r3 = ModPol(43, 4, [39, 35, 35, 25])
        self.assertNotEqual(r0, r3)

    def test_add(self):
        # Example from slide 26
        f = ModPol(41, 4, [32, 0, 17, 22])
        g = ModPol(41, 4, [11, 7, 19, 1])
        # result computed manually
        s = ModPol(41, 4, [2, 7, 36, 23])
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 26
        f = ModPol(41, 4, [32, 0, 17, 22])
        g = ModPol(41, 4, [11, 7, 19, 1])
        # results computed manually
        d1 = ModPol(41, 4, [21, 34, 39, 21])
        d2 = ModPol(41, 4, [-21, -34, -39, -21])
        self.assertEqual(f - g, d1)
        self.assertEqual(g - f, d2)

    def test_mul(self):
        # Example from slide 26
        f = ModPol(41, 4, [32, 0, 17, 22])
        g = ModPol(41, 4, [11, 7, 19, 1])
        r = ModPol(41, 4, [39, 35, 35, 24])
        self.assertEqual(f * g, r)
        self.assertEqual(g * f, r)

    def test_size(self):
        # Examples from slide 35
        f = ModPol(41, 4, [1, 1, -2, 2])
        g = ModPol(41, 4, [-2, 0, 2, -1])
        self.assertEqual(f.size(), 2)
        self.assertEqual(g.size(), 2)
        self.assertEqual((f * g).size(), 8)

    @unittest.skip("slow")
    def test_kyber_ring_is_not_an_integral_domain(self):
        # All 3 Kyber/ML-KEM sizes have q = 3329 (a prime number), n = 256.
        # The resulting ring R_q is not an integral domain, that is,
        # we can find non-zero elements whose product is zero.
        #
        # One way to obtain such elements is the factorisation of
        # the modulus X^256 + 1 over GF(3329).
        # All factors happen to be of the form X^2 + c for some constant c.
        # fmt: off
        constants = [
            17, 48, 109, 233, 268, 279, 314, 319,
            375, 394, 403, 525, 540, 554, 556, 561,
            568, 583, 641, 642, 667, 680, 723, 733,
            735, 756, 757, 780, 863, 885, 886, 892,
            939, 941, 952, 992, 1021, 1026, 1029, 1031,
            1041, 1063, 1092, 1100, 1143, 1173, 1175, 1179,
            1212, 1219, 1230, 1239, 1292, 1409, 1455, 1461,
            1482, 1540, 1584, 1607, 1626, 1637, 1645, 1651,
            1678, 1684, 1692, 1703, 1722, 1745, 1789, 1847,
            1868, 1874, 1920, 2037, 2090, 2099, 2110, 2117,
            2150, 2154, 2156, 2186, 2229, 2237, 2266, 2288,
            2298, 2300, 2303, 2308, 2337, 2377, 2388, 2390,
            2437, 2443, 2444, 2466, 2549, 2572, 2573, 2594,
            2596, 2606, 2649, 2662, 2687, 2688, 2746, 2761,
            2768, 2773, 2775, 2789, 2804, 2926, 2935, 2954,
            3010, 3015, 3050, 3061, 3096, 3220, 3281, 3312,
        ]
        # fmt: on
        factors = [ModPol(3329, 256, [c, 0, 1] + [0] * 253) for c in constants]

        zero = ModPol(3329, 256, [0] * 256)
        one = ModPol(3329, 256, [1] + [0] * 255)

        self.assertEqual(math.prod(factors, start=one), zero)


class VecTest(unittest.TestCase):
    # Example from slide 29
    a = Vec(
        ModPol(137, 4, [93, 51, 34, 54]),
        ModPol(137, 4, [27, 87, 81, 6]),
        ModPol(137, 4, [112, 15, 46, 122]),
    )
    b = Vec(
        ModPol(137, 4, [40, 78, 1, 119]),
        ModPol(137, 4, [11, 31, 57, 90]),
        ModPol(137, 4, [108, 72, 47, 14]),
    )
    s = Vec(
        ModPol(137, 4, [133, 129, 35, 36]),
        ModPol(137, 4, [38, 118, 1, 96]),
        ModPol(137, 4, [83, 87, 93, 136]),
    )
    d = Vec(
        ModPol(137, 4, [53, 110, 33, 72]),
        ModPol(137, 4, [16, 56, 24, 53]),
        ModPol(137, 4, [4, 80, 136, 108]),
    )
    p = ModPol(137, 4, [93, 59, 44, 132])

    def test_equal(self):
        self.assertEqual(self.a, self.a)
        self.assertEqual(self.b, self.b)

        self.assertNotEqual(self.a, self.b)
        self.assertNotEqual(self.b, self.a)

    def test_add(self):
        self.assertEqual(self.a + self.b, self.s)
        self.assertEqual(self.b + self.a, self.s)

    def test_sub(self):
        self.assertEqual(self.a - self.b, self.d)

    def test_mul(self):
        self.assertEqual(self.a * self.b, self.p)
        self.assertEqual(self.b * self.a, self.p)

    def test_size(self):
        # ModPol examples from slide 35 - let's create vectors out of them.
        f = ModPol(41, 4, [1, 1, -2, 2])
        g = ModPol(41, 4, [-2, 0, 2, -1])

        self.assertEqual(Vec(f, g).size(), 2)
        self.assertEqual(Vec(g, f).size(), 2)
        self.assertEqual(Vec(f, g, f).size(), 2)
        self.assertEqual(Vec(g, f, g, f).size(), 2)

        self.assertEqual(Vec(f, g, f * g).size(), 8)
        self.assertEqual(Vec(f, f * g, g).size(), 8)
        self.assertEqual(Vec(f * g, f, g).size(), 8)


class MatTest(unittest.TestCase):
    def test_mlwe(self):
        # Example from slide 39
        def P(*c):
            return ModPol(541, 4, c)

        a = Mat(
            Vec(P(442, 502, 513, 15), P(368, 166, 37, 135)),
            Vec(P(479, 532, 116, 41), P(12, 139, 385, 409)),
            Vec(P(29, 394, 503, 389), P(9, 499, 92, 254)),
        )
        s = Vec(P(2, -2, 0, 1), P(3, -2, -2, -2))
        e = Vec(P(2, -2, -1, 0), P(1, 2, 2, 1), P(-2, 0, -1, -2))
        t = Vec(P(30, 252, 401, 332), P(247, 350, 259, 485), P(534, 234, 137, 443))

        self.assertEqual(t, a @ s + e)

        self.assertEqual(s.size(), 3)
        self.assertEqual(e.size(), 2)
        self.assertEqual(t.size(), 259)
