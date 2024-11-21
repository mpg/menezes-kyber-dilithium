"""
Implementation of a simplified version of Kyber.
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
    """Generate a keypair for "full" Kyber-PKE (slide 65)."""
    # This is K-PKE.GenKey except for the parts related to NTT
    # and serialization of the outputs.
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
    """Encrypt m with "full" Kyber-PKE (slide 66)."""

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
    """Decrypt ciphertext with "full" Kyber-PKE (slide 66)."""
    c1 = c[: 32 * du * k]
    c2 = c[32 * du * k :]

    ud = KVec.decompress_from_bytes(du, c1)
    vd = KModPol.decompress_from_bytes(dv, c2)

    s = KVec.from_bytes(dk_pke)

    w = vd - s * ud
    m = w.compress_to_bytes(1)

    return m
