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

# Kyber-768
k = 3
eta1 = 2
eta2 = 2
du = 10
dv = 4


def genkey(d):
    """Kyber-PKE key generation."""
    # Algorithm 13 K-PKE.KeyGen

    rho, sigma = G(d + k.to_bytes(1))
    prf = PRF(sigma)

    A = KMat.uni_from_seed(k, rho)

    s = KVec.cbd_from_prf(k, eta1, prf)
    e = KVec.cbd_from_prf(k, eta2, prf)

    t = A @ s + e

    ek_pke = t.to_bytes() + rho
    dk_pke = s.to_bytes()

    return (ek_pke, dk_pke)


def encrypt(ek_pke, m, r):
    """Kyber-PKE encryption."""
    # Algorithm 14 K-PKE.Encrypt

    t = KVec.from_bytes(ek_pke[: 384 * k])
    rho = ek_pke[384 * k :]

    A = KMat.uni_from_seed(k, rho)

    prf = PRF(r)
    r = KVec.cbd_from_prf(k, eta1, prf)
    e1 = KVec.cbd_from_prf(k, eta2, prf)
    e2 = KModPol.cbd_from_prf(eta2, prf)

    mu = KModPol.decompress_from_bytes(1, m)

    u = A.transpose() @ r + e1
    v = t * r + e2 + mu

    c1 = u.compress_to_bytes(du)
    c2 = v.compress_to_bytes(dv)

    return c1 + c2


def decrypt(dk_pke, c):
    """Kyber-PKE decryption."""
    # Algorithm 15 K-PKE.Decrypt

    c1 = c[: 32 * du * k]
    c2 = c[32 * du * k :]

    ud = KVec.decompress_from_bytes(du, c1)
    vd = KModPol.decompress_from_bytes(dv, c2)

    s = KVec.from_bytes(dk_pke)

    w = vd - s * ud
    m = w.compress_to_bytes(1)

    return m
