import unittest

from kyber_math import KModInt, KModPol, KVec, KMat
from kyber_sym import PRF

from test_common import get


def kmodpol(c):
    """Helper building a KModPol from a list of int (not KModInt)."""
    q, n = 3329, 256
    return KModPol(q, n, [KModInt(a, q) for a in c])


class KModPolTest(unittest.TestCase):
    def test_to_bytes_and_from_bytes(self):
        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"

            for name in "A[0, 0]", "s[0]", "v":
                coeffs, ref_bytes = get(filename, name)
                pol = kmodpol(coeffs)

                self.assertEqual(pol.to_bytes(), ref_bytes)
                self.assertEqual(KModPol.from_bytes(ref_bytes), pol)

    def test_compress_to_bytes(self):
        for bits, dv in ((512, 4), (768, 4), (1024, 5)):
            filename = f"ML-KEM-{bits}.txt"

            _, v_bytes = get(filename, "v")
            ref_c2 = get(filename, "c2")

            v = KModPol.from_bytes(v_bytes)
            self.assertEqual(v.compress_to_bytes(dv), ref_c2)

    def test_decompress_from_bytes(self):
        for bits, dv in ((512, 4), (768, 4), (1024, 5)):
            filename = f"ML-KEM-{bits}.txt"

            c2 = get(filename, "c2")
            ref_vd = get(filename, "vᵈ")

            got_vd = KModPol.decompress_from_bytes(dv, c2)
            self.assertEqual(got_vd.to_bytes(), ref_vd)

    def test_uni_from_seed(self):
        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp_i, _ = get(filename, "A[0, 0]")
            B = rho + bytes.fromhex("0000")
            gen = KModPol.uni_from_seed(B)
            self.assertEqual(gen, kmodpol(exp_i))

    def test_cbd_from_prf(self):
        for bits, eta1 in ((512, 3), (768, 2), (1024, 2)):
            filename = f"ML-KEM-{bits}.txt"

            sigma = get(filename, "σ")
            ref_s0_coef, _ = get(filename, "s[0]")
            ref_s0 = kmodpol(ref_s0_coef)

            prf = PRF(sigma)
            got_s0 = KModPol.cbd_from_prf(eta1, prf)
            self.assertEqual(got_s0, ref_s0)


class KVecTest(unittest.TestCase):
    def test_from_bytes_to_bytes(self):
        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"
            for varname in "s", "e", "t", "u", "uᵈ":
                ref = get(filename, varname)
                self.assertEqual(KVec.from_bytes(ref).to_bytes(), ref)

    def test_compress_to_bytes(self):
        for bits, du in ((512, 10), (768, 10), (1024, 11)):
            filename = f"ML-KEM-{bits}.txt"

            u_bytes = get(filename, "u")
            ref_c1 = get(filename, "c1")

            u = KVec.from_bytes(u_bytes)
            self.assertEqual(u.compress_to_bytes(du), ref_c1)

    def test_decompress_from_bytes(self):
        for bits, du in ((512, 10), (768, 10), (1024, 11)):
            filename = f"ML-KEM-{bits}.txt"

            c1 = get(filename, "c1")
            ref_ud = get(filename, "uᵈ")

            got_ud = KVec.decompress_from_bytes(du, c1)
            self.assertEqual(got_ud.to_bytes(), ref_ud)

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
    def test_uni_from_seed_and_to_bytes(self):
        for bits, k in ((512, 2), (768, 3), (1024, 4)):
            filename = f"ML-KEM-{bits}.txt"

            rho = get(filename, "ρ")
            exp = get(filename, "A")
            got = KMat.uni_from_seed(k, rho).to_bytes()
            self.assertEqual(got, exp)
