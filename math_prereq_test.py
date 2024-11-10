import unittest

from math_prereq import (
    ModInt,
    ModPol,
    Vec,
    Mat,
)


def get(filename, varname):
    prefix = varname + " = "
    with open(filename, encoding="utf8") as f:
        for line in f:
            if line.startswith(prefix):
                val = line.strip()[len(prefix) :]
                break
    # is this a list of integers?
    if val[0] == "{":
        end = val.find("}")
        lst = [int(v) for v in val[1:end].split(", ")]
        # the list is followed by its serialized version
        start = end + len("} = ")
        ser = bytes.fromhex(val[start:])

        return lst, ser

    # if not, it must be bytes
    return bytes.fromhex(val)


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

    def test_round(self):
        self.assertEqual(ModInt(0, 4).round(), 0)
        self.assertEqual(ModInt(1, 4).round(), 1)
        self.assertEqual(ModInt(2, 4).round(), 1)
        self.assertEqual(ModInt(3, 4).round(), 1)

        # example from slide 47
        self.assertEqual(ModInt(-832, 3329).round(), 0)
        self.assertEqual(ModInt(832, 3329).round(), 0)
        self.assertEqual(ModInt(-833, 3329).round(), 1)
        self.assertEqual(ModInt(833, 3329).round(), 1)

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        seen0, seen1, seen2 = 0, 0, 0
        times = 30
        for _ in range(times):
            r = ModInt.rand_uni(3)
            if r == ModInt(0, 3):
                seen0 += 1
            if r == ModInt(1, 3):
                seen1 += 1
            if r == ModInt(2, 3):
                seen2 += 1
        self.assertNotEqual(seen0, 0)
        self.assertNotEqual(seen1, 0)
        self.assertNotEqual(seen2, 0)
        self.assertEqual(seen0 + seen1 + seen2, times)

    def test_rand_small_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        seen0, seen1, seen2, seenm1, seenm2 = 0, 0, 0, 0, 0
        times = 50
        q = 3329
        for _ in range(times):
            r = ModInt.rand_small_uni(q, 2)
            if r == ModInt(0, q):
                seen0 += 1
            if r == ModInt(1, q):
                seen1 += 1
            if r == ModInt(2, q):
                seen2 += 1
            if r == ModInt(-1, q):
                seenm1 += 1
            if r == ModInt(-2, q):
                seenm2 += 1
        self.assertNotEqual(seen0, 0)
        self.assertNotEqual(seen1, 0)
        self.assertNotEqual(seen2, 0)
        self.assertNotEqual(seenm1, 0)
        self.assertNotEqual(seenm2, 0)
        self.assertEqual(seen0 + seen1 + seen2 + seenm1 + seenm2, times)


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

    def test_round(self):
        # Example from slide 47
        f = ModPol(3329, 4, [3000, 1500, 2010, 37])
        g = [0, 1, 1, 0]
        self.assertEqual(f.round(), g)

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n = 17, 8
        for _ in range(100):
            f = ModPol.rand_uni(q, n)
            max_size = max(max_size, f.size())
        self.assertEqual(max_size, q // 2)

        # Ensure we get objects of the right shape
        q, n = 3, 2
        zero = ModPol(q, n, [0, 0])  # proba 1 / 3^2
        seen0 = False
        for _ in range(100):
            seen0 |= ModPol.rand_uni(q, n) == zero
        self.assertTrue(seen0)

    def test_rand_small_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, eta = 3329, 8, 3
        for _ in range(100):
            f = ModPol.rand_small_uni(q, n, eta)
            max_size = max(max_size, f.size())
        self.assertEqual(max_size, eta)

        # Ensure we get objects of the right shape
        q, n, eta = 3329, 2, 1
        zero = ModPol(q, n, [0, 0])  # proba 1 / 3^2
        seen0 = False
        for _ in range(100):
            seen0 |= ModPol.rand_small_uni(q, n, eta) == zero
        self.assertTrue(seen0)

    def test_from_seed_and_to_bytes(self):
        q, n = 3329, 256

        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp_i, exp_b = get(filename, "A[0, 0]")
            B = rho + bytes.fromhex("0000")
            gen = ModPol.from_seed(q, n, B)
            self.assertEqual(gen, ModPol(q, n, exp_i))
            self.assertEqual(gen.to_bytes(), exp_b)


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

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k = 17, 8, 3
        for _ in range(30):
            v = Vec.rand_uni(q, n, k)
            max_size = max(max_size, v.size())
        self.assertEqual(max_size, q // 2)

        # Ensure we get objects of the right shape
        q, n, k = 3, 2, 1
        zero = Vec(ModPol(q, n, [0, 0]))  # proba 1 / 3^(2*1)
        seen0 = False
        for _ in range(100):
            seen0 |= Vec.rand_uni(q, n, k) == zero
        self.assertTrue(seen0)

    def test_rand_small_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k, eta = 3329, 8, 2, 3
        for _ in range(50):
            v = Vec.rand_small_uni(q, n, k, eta)
            max_size = max(max_size, v.size())
        self.assertEqual(max_size, eta)

        # Ensure we get objects of the right shape
        q, n, k, eta = 3329, 3, 2, 1
        zeropol = ModPol(q, n, [0, 0, 0])  # 1 / 3^3
        zero = Vec(zeropol, zeropol)  # proba 1 / 3^(3*2) = 1 / 729
        seen0 = False
        for _ in range(10000):
            seen0 |= Vec.rand_small_uni(q, n, k, eta) == zero
        self.assertTrue(seen0)


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

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k = 17, 8, 3
        for _ in range(10):
            m = Mat.rand_uni(q, n, k)
            sizes = [v.size() for v in m.lines]
            max_size = max(max_size, *sizes)
        self.assertEqual(max_size, q // 2)

        # Ensure we get objects of the right shape
        q, n, k = 3, 2, 1
        zero = Mat(Vec(ModPol(q, n, [0, 0])))  # proba 1 / 3^(2*1)
        seen0 = False
        for _ in range(100):
            seen0 |= Mat.rand_uni(q, n, k) == zero
        self.assertTrue(seen0)

    def test_transpose(self):
        a = ModPol(6, 1, [0])
        b = ModPol(6, 1, [1])
        c = ModPol(6, 1, [2])
        d = ModPol(6, 1, [3])
        e = ModPol(6, 1, [4])
        f = ModPol(6, 1, [5])

        m1 = Mat(Vec(a, b), Vec(c, d))
        m2 = Mat(Vec(a, c), Vec(b, d))
        self.assertEqual(m1.transpose(), m2)
        self.assertEqual(m2.transpose(), m1)

        m1 = Mat(Vec(a, b, c), Vec(d, e, f))
        m2 = Mat(Vec(a, d), Vec(b, e), Vec(c, f))
        self.assertEqual(m1.transpose(), m2)
        self.assertEqual(m2.transpose(), m1)

    def test_from_seed_and_to_bytes(self):
        q, n = 3329, 256

        for bits, k in ((512, 2), (768, 3), (1024, 4)):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp = get(filename, "A")
            got = Mat.from_seed(q, n, k, rho).to_bytes()
            self.assertEqual(got, exp)
