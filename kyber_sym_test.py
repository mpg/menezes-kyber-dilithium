import unittest

from kyber_sym import G, H, J

from test_common import get


class GTest(unittest.TestCase):
    def test_kpke_keygen(self):
        # Test G() as used in K-PKE.KeyGen: (rho, sigma) := G(d||k)
        # Well actually the intermediate values we have are still based on the
        # initial public draft which differs from the final version on this:
        # (rho, sigma) := G(d)
        for bits, k in ((512, 2), (768, 3), (1024, 4)):
            filename = f"ML-KEM-{bits}.txt"
            d = get(filename, "d")
            ref_rho = get(filename, "ρ")
            ref_sigma = get(filename, "σ")

            c = d + k.to_bytes(1)
            c = c[:-1]  # see comment above
            got_rho, got_sigma = G(c)

            self.assertEqual(got_rho, ref_rho)
            self.assertEqual(got_sigma, ref_sigma)

    def test_kem_encaps_internal(self):
        # Test G() as used in ML-KEM.Encaps_internal: (K, r) := G(m || H(ek))
        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"
            m = get(filename, "m")
            h_ek = get(filename, "H(ek)")
            ref_K = get(filename, "K")
            ref_r = get(filename, "r")

            got_K, got_r = G(m + h_ek)

            self.assertEqual(got_K, ref_K)
            self.assertEqual(got_r, ref_r)


class HTest(unittest.TestCase):
    def test_kem_internal(self):
        # Test H() as used in KeyGen_internal and Encaps_internal: H(ek)
        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"
            ek = get(filename, "ek")
            h_ek = get(filename, "H(ek)")

            self.assertEqual(H(ek), h_ek)


class JTest(unittest.TestCase):
    def test_kem_internal(self):
        # Test J() as used in Decaps_internal: Kbar := J(z || c)
        for bits in (512, 768, 1024):
            filename = f"ML-KEM-{bits}.txt"

            z = get(filename, "z")
            c = get(filename, "c")
            k_bar = get(filename, "KBar")

            self.assertEqual(J(z + c), k_bar)
