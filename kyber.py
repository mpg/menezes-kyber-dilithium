"""
Implementation of a simplified version of Kyber.
"""

from kyber_math import KModPol, KVec, KMat
from kyber_aux import G, PRF

# Kyber (all sizes)
q = 3329
n = 256
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

    A = KMat.from_seed(q, n, k, rho)

    s = KVec.cbd_from_prf(k, eta1, prf)
    e = KVec.cbd_from_prf(k, eta2, prf)

    t = A @ s + e

    return ((rho, t), s)


def encrypt(pub, msg, r):
    """Encrypt msg (list of 0, 1) with "full" Kyber-PKE (slide 66)."""
    # This is K-PKE.Encrypt except for the parts related to NTT
    # and (de)serialization of the inputs and outputs.
    if len(msg) != n or any(b not in (0, 1) for b in msg):
        raise ValueError

    rho, t = pub
    A = KMat.from_seed(q, n, k, rho)

    prf = PRF(r)
    r = KVec.cbd_from_prf(k, eta1, prf)
    e1 = KVec.cbd_from_prf(k, eta2, prf)
    e2 = KModPol.cbd_from_prf(eta2, prf)

    mu = KModPol.decompress(q, n, msg, 1)

    u = A.transpose() @ r + e1
    v = t * r + e2 + mu

    c1 = u.compress(du)
    c2 = v.compress(dv)

    return (c1, c2)


def decrypt(prv, ct):
    """Decrypt ciphertext with "full" Kyber-PKE (slide 66)."""
    s = prv
    c1, c2 = ct

    uu = KVec.decompress(q, n, c1, du)
    vv = KModPol.decompress(q, n, c2, dv)

    return (vv - s * uu).compress(1)
