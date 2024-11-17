import unittest

from kyber_math import KModInt, KModPol, KVec, KMat


def get(filename, varname):
    """Read a value from a ML-KEM-*.txt file."""
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


def kmodpol(q, n, c):
    """Helper building a KModPol from a list of int (not KModInt)."""
    return KModPol(q, n, [KModInt(a, q) for a in c])


class KModIntTest(unittest.TestCase):
    def test_round(self):
        self.assertEqual(KModInt(0, 4).round(), 0)
        self.assertEqual(KModInt(1, 4).round(), 1)
        self.assertEqual(KModInt(2, 4).round(), 1)
        self.assertEqual(KModInt(3, 4).round(), 1)

        # example from slide 47
        self.assertEqual(KModInt(-832, 3329).round(), 0)
        self.assertEqual(KModInt(832, 3329).round(), 0)
        self.assertEqual(KModInt(-833, 3329).round(), 1)
        self.assertEqual(KModInt(833, 3329).round(), 1)

    def test_compress_decompress(self):
        # slide 58
        q, d = 19, 2
        data = [
            (0, 0, 0),
            (1, 0, 0),
            (2, 0, 0),
            (3, 1, 5),
            (4, 1, 5),
            (5, 1, 5),
            (6, 1, 5),
            (7, 1, 5),
            (8, 2, 10),
            (9, 2, 10),
            (10, 2, 10),
            (11, 2, 10),
            (12, 3, 14),
            (13, 3, 14),
            (14, 3, 14),
            (15, 3, 14),
            (16, 3, 14),
            (17, 0, 0),
            (18, 0, 0),
        ]
        for x, y, x1 in data:
            self.assertEqual(KModInt(x, q).compress(d), y)
            self.assertEqual(KModInt.decompress(q, y, d), KModInt(x1, q))

    def test_rand_small_cbd(self):
        # Don't actually test the distribution,
        # only the output range.
        seen0, seen1, seen2, seenm1, seenm2 = 0, 0, 0, 0, 0
        times = 100
        q = 3329
        for _ in range(times):
            r = KModInt.rand_small_cbd(q, 2)
            if r == KModInt(0, q):
                seen0 += 1
            if r == KModInt(1, q):
                seen1 += 1
            if r == KModInt(2, q):
                seen2 += 1
            if r == KModInt(-1, q):
                seenm1 += 1
            if r == KModInt(-2, q):
                seenm2 += 1
        self.assertNotEqual(seen0, 0)
        self.assertNotEqual(seen1, 0)
        self.assertNotEqual(seen2, 0)
        self.assertNotEqual(seenm1, 0)
        self.assertNotEqual(seenm2, 0)
        self.assertEqual(seen0 + seen1 + seen2 + seenm1 + seenm2, times)


class KModPolTest(unittest.TestCase):
    def test_round(self):
        # Example from slide 47
        f = kmodpol(3329, 4, [3000, 1500, 2010, 37])
        g = [0, 1, 1, 0]
        self.assertEqual(f.round(), g)

    def test_rand_small_cbd(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, eta = 3329, 8, 3
        for _ in range(100):
            f = KModPol.rand_small_cbd(q, n, eta)
            max_size = max(max_size, f.size())
        self.assertEqual(max_size, eta)

        # Ensure we get objects of the right shape
        q, n, eta = 3329, 2, 1
        zero = kmodpol(q, n, [0, 0])  # proba 1 / 2^2
        seen0 = False
        for _ in range(50):
            seen0 |= KModPol.rand_small_cbd(q, n, eta) == zero
        self.assertTrue(seen0)

    def test_from_seed_and_to_bytes(self):
        q, n = 3329, 256

        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp_i, exp_b = get(filename, "A[0, 0]")
            B = rho + bytes.fromhex("0000")
            gen = KModPol.from_seed(q, n, B)
            self.assertEqual(gen, kmodpol(q, n, exp_i))
            self.assertEqual(gen.to_bytes(), exp_b)

    def test_compress_decompress(self):
        # slides 59 and 60
        q, n = 3329, 4
        f = kmodpol(q, n, [223, 1438, 3280, 798])

        g10 = [69, 442, 1009, 245]
        h10 = kmodpol(q, n, [224, 1437, 3280, 796])
        self.assertEqual(f.compress(10), g10)
        self.assertEqual(KModPol.decompress(q, n, g10, 10), h10)

        g4 = [1, 7, 0, 4]
        h4 = kmodpol(q, n, [208, 1456, 0, 832])
        self.assertEqual(f.compress(4), g4)
        self.assertEqual(KModPol.decompress(q, n, g4, 4), h4)


class KVecTest(unittest.TestCase):
    def test_rand_small_cbd(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k, eta = 3329, 8, 2, 3
        for _ in range(50):
            v = KVec.rand_small_cbd(q, n, k, eta)
            max_size = max(max_size, v.size())
        self.assertEqual(max_size, eta)

        # Ensure we get objects of the right shape
        q, n, k, eta = 3329, 3, 2, 1
        zeropol = kmodpol(q, n, [0, 0, 0])  # 1 / 2^3
        zero = KVec([zeropol, zeropol])  # proba 1 / 2^(3*2) = 1 / 64
        seen0 = False
        for _ in range(1000):
            seen0 |= KVec.rand_small_cbd(q, n, k, eta) == zero
        self.assertTrue(seen0)

    def test_compress_decompress(self):
        # recycle examples from slide 59 and 60
        q, n = 3329, 4

        fc = [223, 1438, 3280, 798]
        f = KVec([kmodpol(q, n, fc), kmodpol(q, n, list(reversed(fc)))])

        data = (
            (10, [69, 442, 1009, 245], [224, 1437, 3280, 796]),
            (4, [1, 7, 0, 4], [208, 1456, 0, 832]),
        )

        for d, g1, hc in data:
            g = [g1, list(reversed(g1))]
            self.assertEqual(f.compress(d), g)

            h = KVec([kmodpol(q, n, hc), kmodpol(q, n, list(reversed(hc)))])
            self.assertEqual(KVec.decompress(q, n, g, d), h)


class KMatTest(unittest.TestCase):
    def test_from_seed_and_to_bytes(self):
        q, n = 3329, 256

        for bits, k in ((512, 2), (768, 3), (1024, 4)):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp = get(filename, "A")
            got = KMat.from_seed(q, n, k, rho).to_bytes()
            self.assertEqual(got, exp)
