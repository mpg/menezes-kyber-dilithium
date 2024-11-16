"""
Implementation of a simplified version of Kyber.
"""

import secrets

from math_prereq import Vec, KMat, ModPol, ModInt

# Kyber (all sizes)
q = 3329
n = 256
# Kyber-768
k = 3
eta1 = 2
eta2 = 2
du = 10
dv = 4


def genkey():
    """Generate a keypair for "full" Kyber-PKE (slide 65)."""
    rho = secrets.token_bytes(32)
    A = KMat.from_seed(q, n, k, rho)

    s = Vec.rand_small_cbd(q, n, k, eta1)
    e = Vec.rand_small_cbd(q, n, k, eta2)

    t = A @ s + e

    return ((rho, t), s)


def encrypt(pub, msg):
    """Encrypt msg (list of 0, 1) with "full" Kyber-PKE (slide 66)."""
    if len(msg) != n or any(b not in (0, 1) for b in msg):
        raise ValueError

    rho, t = pub
    A = KMat.from_seed(q, n, k, rho)

    r = Vec.rand_small_cbd(q, n, k, eta1)
    e1 = Vec.rand_small_cbd(q, n, k, eta2)
    e2 = ModPol.rand_small_cbd(q, n, eta2)

    # q2m := ⌈q/2⌋ * m
    q2 = q // 2 + 1  # we know q is odd
    q2m = ModPol(q, n, [ModInt(b * q2, q) for b in msg])

    u = A.transpose() @ r + e1
    v = t * r + e2 + q2m

    c1 = u.compress(du)
    c2 = v.compress(dv)

    return (c1, c2)


def decrypt(prv, ct):
    """Decrypt ciphertext with "full" Kyber-PKE (slide 66)."""
    s = prv
    c1, c2 = ct

    uu = Vec.decompress(q, n, c1, du)
    vv = ModPol.decompress(q, n, c2, dv)

    return (vv - s * uu).round()
