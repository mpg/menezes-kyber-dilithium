"""
Implementation of a simplified (no NTT) version of Kyber.

This is what Kyber would probably look like if the decision had been made
not to bake the NTT into the standard. I follow the lectures, and the NTT
comes at the end, so I won't have a compliant implementation until the end.

Based the spec¹ - except for the parts related to the NTT.
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

For a version closer to the lectures/slides, see previous commits.
"""

import secrets

from kyber_math import KModPol, KVec, KMat
from kyber_sym import PRF, G, H, J


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

    def keygen(self, d):
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


class KyberKEM:
    """A simplified version (no NTT) of the Kyber KEM."""

    def __init__(self, param_set):
        """Initialize the Kyber KEM with the given parameter set."""
        self.pke = KyberPKE(param_set)

    def keygen_internal(self, d, z):
        """Kyber-KEM internal KeyGen."""
        # Algorithm 16 ML-KEM.KeyGen_internal

        ek_pke, dk_pke = self.pke.keygen(d)

        ek = ek_pke
        dk = dk_pke + ek + H(ek) + z

        return ek, dk

    def encaps_internal(self, ek, m):
        """Kyber-KEM internal Encaps."""
        # Algorithm 17 ML-KEM.Encaps_internal

        K, r = G(m + H(ek))
        c = self.pke.encrypt(ek, m, r)

        return (K, c)

    def decaps_internal(self, dk, c):
        """Kyber-KEM internal Decaps."""
        # Algorithm 18 ML-KEM.Decaps_internal

        k = self.pke.k
        dk_pke = dk[0 : 384 * k]
        ek_pke = dk[384 * k : 768 * k + 32]
        h = dk[768 * k + 32 : 768 * k + 64]
        z = dk[768 * k + 64 : 768 * k + 96]

        m_prime = self.pke.decrypt(dk_pke, c)

        K_prime, r_prime = G(m_prime + h)
        c_prime = self.pke.encrypt(ek_pke, m_prime, r_prime)
        if c_prime != c:
            return J(z + c)

        return K_prime

    def keygen(self):
        """Kyber-KEM KeyGen."""
        # Algorithm 19 ML-KEM.KeyGen
        d = secrets.token_bytes(32)
        z = secrets.token_bytes(32)
        return self.keygen_internal(d, z)

    def encaps(self, ek):
        """Kyber-KEM Encaps."""
        # Algorithm 20 ML-KEM.Encaps
        m = secrets.token_bytes(32)
        return self.encaps_internal(ek, m)

    def decaps(self, dk, c):
        """Kyber-KEM Decaps."""
        # Algorithm 21 ML-KEM.Decaps
        return self.decaps_internal(dk, c)
