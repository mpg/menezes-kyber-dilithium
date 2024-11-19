import unittest

from kyber_math import KModInt, KModPol, KVec, KMat
from kyber_aux import PRF

from test_common import get


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


class KModPolTest(unittest.TestCase):
    def test_round(self):
        # Example from slide 47
        f = kmodpol(3329, 4, [3000, 1500, 2010, 37])
        g = [0, 1, 1, 0]
        self.assertEqual(f.round(), g)

    def test_cbd_from_prf(self):
        q, n = 3329, 256
        for bits, eta1 in ((512, 3), (768, 2), (1024, 2)):
            filename = f"ML-KEM-{bits}.txt"

            sigma = get(filename, "σ")
            ref_s0_coef, _ = get(filename, "s[0]")
            ref_s0 = kmodpol(q, n, ref_s0_coef)

            prf = PRF(sigma)
            got_s0 = KModPol.cbd_from_prf(eta1, prf)
            self.assertEqual(got_s0, ref_s0)

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

    def test_cbd_from_prf_keygen(self):
        # Simulates steps from K-PKE.KeyGen
        for bits, eta1, k in ((512, 3, 2), (768, 2, 3), (1024, 2, 4)):
            filename = f"ML-KEM-{bits}.txt"

            sigma = get(filename, "σ")
            ref_s = get(filename, "s")
            ref_e = get(filename, "e")

            prf = PRF(sigma)
            got_s = KVec.cbd_from_prf(k, eta1, prf)
            got_e = KVec.cbd_from_prf(k, eta1, prf)

            self.assertEqual(got_s.to_bytes(), ref_s)
            self.assertEqual(got_e.to_bytes(), ref_e)

    def test_cbd_from_prf_encrypt(self):
        eta2 = 2
        # Simulates steps from K-PKE.Encrypt
        for bits, eta1, k in ((512, 3, 2), (768, 2, 3), (1024, 2, 4)):
            filename = f"ML-KEM-{bits}.txt"

            r = get(filename, "r")
            ref_y = get(filename, "y")
            ref_e1 = get(filename, "e1")
            ref_e2 = get(filename, "e2")

            prf = PRF(r)
            got_y = KVec.cbd_from_prf(k, eta1, prf)
            got_e1 = KVec.cbd_from_prf(k, eta2, prf)
            got_e2 = KModPol.cbd_from_prf(eta2, prf)

            self.assertEqual(got_y.to_bytes(), ref_y)
            self.assertEqual(got_e1.to_bytes(), ref_e1)
            self.assertEqual(got_e2.to_bytes(), ref_e2)


class KMatTest(unittest.TestCase):
    def test_from_seed_and_to_bytes(self):
        q, n = 3329, 256

        for bits, k in ((512, 2), (768, 3), (1024, 4)):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp = get(filename, "A")
            got = KMat.from_seed(q, n, k, rho).to_bytes()
            self.assertEqual(got, exp)
