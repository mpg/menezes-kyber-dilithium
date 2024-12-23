"""
Extends mathematical objects (from V1b) with Kyber specific methods.

This is section 4.2 from the spec¹: conversion and compression
algorithms (4.2.1), as well as sampling algorithms (4.2.2).
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

For a version closer to the lectures/slides, see previous commits.
"""

from common_math import ModInt, ModPol, Vec, Mat

from kyber_sym import XOF

# Common to all Kyber sizes.
q = 3329
n = 256


def ints_from_bits(d, bits):
    """Turn an iterable of bits into a list of d-bit integers."""
    ints = []
    x = 0
    for i, b in enumerate(bits):
        x += b * 2 ** (i % d)
        if i % d == d - 1:
            ints.append(x)
            x = 0
    return ints


def bits_from_ints(d, ints):
    """Turn an iterable of d-bit integers into a list of bits."""
    bits = []
    for x in ints:
        for _ in range(d):
            bits.append(x % 2)
            x //= 2
    return bits


def bytes_from_bits(b):
    """Algorithm 3 BitsToBytes spec (p. 20)."""
    return b"".join(x.to_bytes(1) for x in ints_from_bits(8, b))


def bits_from_bytes(B):
    """Algorithm 4 BytesToBits from the spec (p. 20)."""
    return bits_from_ints(8, B)


def bytes_from_ints(d, F):
    """Algorithm 5 ByteEncode_d from the spec (p. 22)."""
    return bytes_from_bits(bits_from_ints(d, F))


def ints_from_bytes(d, B):
    """Algorithm 6 ByteDecode_d from the spec (p. 22)."""
    return ints_from_bits(d, bits_from_bytes(B))


class KModInt(ModInt):
    """Modular integer with Kyber extras."""

    def compress(self, d):
        """Compress (slide 57 or Compress_d eq. (4.7) p. 21)."""
        # round() is not what we want as round(0.5) == 0
        # int(0.5 + x) is what we want.
        return int(0.5 + self.r * 2**d / q) % 2**d

    @classmethod
    def decompress(cls, d, y):
        """Decompress (slide 57 or Decompress_d eq. (4.8) p. 21)."""
        # See comment on compress().
        return cls(int(0.5 + y * q / 2**d), q)

    @classmethod
    def cbd_from_bits(cls, eta, bits):
        """Small (size <= eta) modular integer with CBD from bits."""
        # This is lines 3, 4 and 5 (rhs) of Algorithm 8 SamplePolyCBD
        r = sum(bits[:eta]) - sum(bits[eta:])
        return cls(r, q)


class KModPol(ModPol):
    """Element of R_q with Kyber extras."""

    coef_cls = KModInt

    def to_bytes(self):
        """Serialize: ByteEncode_12 from the spec."""
        return bytes_from_ints(12, (int(c_i) for c_i in self.c))

    @classmethod
    def from_bytes(cls, B):
        """Deserialize: ByteDecode_12 from the spec."""
        c = ints_from_bytes(12, B)
        return cls(q, n, [cls.coef_cls(c_i, q) for c_i in c])

    def compress_to_bytes(self, d):
        """Compress and serialize: ByteEncode_d(Compress_d(self))."""
        return bytes_from_ints(d, (c_i.compress(d) for c_i in self.c))

    @classmethod
    def decompress_from_bytes(cls, d, B):
        """Deserialize and decompress: Decompress_d(ByteDecode_d(B))."""
        c = ints_from_bytes(d, B)
        return cls(q, n, [cls.coef_cls.decompress(d, c_i) for c_i in c])

    @classmethod
    def uni_from_seed(cls, B):
        """Generate pseudo-random element of R_q based on a seed."""
        # This is essentially Algorithm 7 SampleNTT from the spec.
        # The algorithm in the spec ouputs 256 elements in Z_q, which are
        # meant to be interpreted as a polynomial in the NTT domain.
        # Here we interpret them as a normal polynomial instead because we
        # haven't implemented NTT yet.

        ctx = XOF()
        ctx.absorb(B)
        a = []
        while len(a) < n:
            C = ctx.squeeze(3)
            # pylint: disable-next=unbalanced-tuple-unpacking
            d1, d2 = ints_from_bytes(12, C)
            if d1 < q:
                a.append(cls.coef_cls(d1, q))
            if d2 < q and len(a) < n:
                a.append(cls.coef_cls(d2, q))

        return cls(q, n, a)

    @classmethod
    def cbd_from_prf(cls, eta, prf):
        """Small (size <= eta) element of R_q using CBD from a PRF."""
        # This is Algorithm 8 SamplePolyCBD_eta, plus the PRF invocation.
        B = prf.next(eta)
        assert len(B) == 64 * eta
        bits = bits_from_bytes(B)
        c = [
            cls.coef_cls.cbd_from_bits(eta, bits[i : i + 2 * eta])
            for i in range(0, len(bits), 2 * eta)
        ]
        return cls(q, n, c)


class KVec(Vec):
    """Element of R_q^k with Kyber extras."""

    item_cls = KModPol

    def to_bytes(self):
        """Serialize."""
        return b"".join(x.to_bytes() for x in self.v)

    @classmethod
    def from_bytes(cls, B):
        """Deserialize."""
        size = 12 * 32  # 12 bits/coeff * 256 coeffs / 8 bits/byte
        chunks = [B[i : i + size] for i in range(0, len(B), size)]
        v = [cls.item_cls.from_bytes(chunk) for chunk in chunks]
        return cls(v)

    def compress_to_bytes(self, d):
        """Compress and serialize."""
        return b"".join(x.compress_to_bytes(d) for x in self.v)

    @classmethod
    def decompress_from_bytes(cls, d, B):
        """Decompress and deserialize."""
        size = d * 32  # d bits/coeff * 256 coeffs / 8 bits/byte
        chunks = [B[i : i + size] for i in range(0, len(B), size)]
        v = [cls.item_cls.decompress_from_bytes(d, chunk) for chunk in chunks]
        return cls(v)

    @classmethod
    def cbd_from_prf(cls, k, eta, prf):
        """Generate a pseudo-random CBD small vector from a PRF."""
        # This is the loops in Algorithm 13 lines 8-11 and 12-15
        # and Algorithm 14 lines 9-12 and 13-16.
        v = [cls.item_cls.cbd_from_prf(eta, prf) for _ in range(k)]
        return cls(v)


class KMat(Mat):
    """Matrix of elements of R_q with Kyber extras."""

    line_cls = KVec
    item_cls = KModPol

    def to_bytes(self):
        """Serialize (line-wise, only used in tests)."""
        return b"".join(l.to_bytes() for l in self.lines)

    @classmethod
    def uni_from_seed(cls, k, rho):
        """Generate pseudo-random square matrix based on a seed."""
        # This is lines 3-7 in Algorithm 13 K-PKE.KeyGen or equivalently
        # lines 4-8 in Algorithm 14 K-PKE.Encrypt in the spec,
        # except the result is supposed to be interpret it as in the NTT
        # domain, but we interpret it as normal polynomials instead
        # because we haven't implementet NTT yet.
        a = []
        for i in range(k):
            a_i = []
            for j in range(k):
                B = rho + j.to_bytes(1) + i.to_bytes(1)
                a_ij = cls.item_cls.uni_from_seed(B)
                a_i.append(a_ij)
            a.append(cls.line_cls(a_i))

        return cls(a)
