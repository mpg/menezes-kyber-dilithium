"""
Implementation of a simplified version of Kyber.
"""

from math_prereq import Vec, Mat, ModPol

# Kyber (all sizes)
q = 3329
n = 256
# Kyber-768
k = 3
eta1 = 2
eta2 = 2


def genkey():
    """Generate a keypair for simplified Kyber-PKE (slide 48)."""
    A = Mat.rand_uni(q, n, k)
    s = Vec.rand_small_uni(q, n, k, eta1)
    e = Vec.rand_small_uni(q, n, k, eta2)
    t = A @ s + e

    return ((A, t), s)


def encrypt(pub, msg):
    """Encrypt msg (list of 0, 1) with simplified Kyber-PKE (slide 49)."""
    if len(msg) != n or any(b not in (0, 1) for b in msg):
        raise ValueError

    A, t = pub

    q2 = q // 2 + 1
    q2m = ModPol(q, n, [b * q2 for b in msg])

    r = Vec.rand_small_uni(q, n, k, eta1)
    e1 = Vec.rand_small_uni(q, n, k, eta2)
    e2 = ModPol.rand_small_uni(q, n, eta2)

    u = A.transpose() @ r + e1
    v = t * r + e2 + q2m

    return (u, v)


def decrypt(prv, ct):
    """Decrypt ciphertext with simplified Kyber-PKE (slide 49)."""
    s = prv
    u, v = ct
    return (v - s * u).round()
