"""
Implementation of a simplified (no NTT) version of Kyber-PKE.

This is what Kyber-PKE would probably look like if the decision had been made
not to bake the NTT into the standard. I follow the lectures, and the NTT
comes at the end, so I won't have a compliant implementation until the end.

Based the spec¹ - except for the parts related to the NTT.
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

For a version closer to the lectures/slides, see previous commits.
"""

from kyber_math import KModPol, KVec, KMat
from kyber_sym import G, PRF


class KyberPKE:
    """A simplified version (no NTT) of Kyber-PKE."""

    def __init__(self, param_set):
        """Initialize the Kyber PKE with the given parameter set."""
        # Table 2 Approved parameter sets for ML-KEM, p. 39
        if param_set == 512:
            self.k = 2
            self.eta1, self.eta2 = 3, 2
            self.du, self.dv = 10, 4
        elif param_set == 768:
            self.k = 3
            self.eta1, self.eta2 = 2, 2
            self.du, self.dv = 10, 4
        elif param_set == 1024:
            self.k = 4
            self.eta1, self.eta2 = 2, 2
            self.du, self.dv = 11, 5
        else:
            raise ValueError

    def genkey(self, d):
        """Kyber-PKE key generation."""
        # Algorithm 13 K-PKE.KeyGen

        rho, sigma = G(d + self.k.to_bytes(1))
        prf = PRF(sigma)

        A = KMat.uni_from_seed(self.k, rho)

        s = KVec.cbd_from_prf(self.k, self.eta1, prf)
        e = KVec.cbd_from_prf(self.k, self.eta2, prf)

        t = A @ s + e

        ek_pke = t.to_bytes() + rho
        dk_pke = s.to_bytes()

        return (ek_pke, dk_pke)

    def encrypt(self, ek_pke, m, r):
        """Kyber-PKE encryption."""
        # Algorithm 14 K-PKE.Encrypt

        t = KVec.from_bytes(ek_pke[: 384 * self.k])
        rho = ek_pke[384 * self.k :]

        A = KMat.uni_from_seed(self.k, rho)

        prf = PRF(r)
        r = KVec.cbd_from_prf(self.k, self.eta1, prf)
        e1 = KVec.cbd_from_prf(self.k, self.eta2, prf)
        e2 = KModPol.cbd_from_prf(self.eta2, prf)

        mu = KModPol.decompress_from_bytes(1, m)

        u = A.transpose() @ r + e1
        v = t * r + e2 + mu

        c1 = u.compress_to_bytes(self.du)
        c2 = v.compress_to_bytes(self.dv)

        return c1 + c2

    def decrypt(self, dk_pke, c):
        """Kyber-PKE decryption."""
        # Algorithm 15 K-PKE.Decrypt

        c1 = c[: 32 * self.du * self.k]
        c2 = c[32 * self.du * self.k :]

        ud = KVec.decompress_from_bytes(self.du, c1)
        vd = KModPol.decompress_from_bytes(self.dv, c2)

        s = KVec.from_bytes(dk_pke)

        w = vd - s * ud
        m = w.compress_to_bytes(1)

        return m
