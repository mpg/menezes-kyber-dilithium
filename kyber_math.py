"""
Extends mathematical objects (from V1b) with Kyber speficic methods.

Some methods follow the lectures, and mention a slide number.
Some methods follow the actual ML-KEM spec¹ and mention it.
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
"""

import secrets

from common_math import ModInt, ModPol, Vec, Mat

from kyber_aux import XOF


class KModInt(ModInt):
    """Modular integer with Kyber extras."""

    @classmethod
    def rand_small_cbd(cls, q, eta):
        """Pick a small (size <= eta) ModInt with central binomial
        distribution (slide 62)."""
        a = [secrets.randbits(1) for _ in range(eta)]
        b = [secrets.randbits(1) for _ in range(eta)]
        c = sum(ai - bi for ai, bi in zip(a, b))
        return cls(c, q)

    def round(self):
        """Rounding (slide 47)."""
        return int(self.q / 4 <= self.r <= 3 * self.q / 4)

    def compress(self, d):
        """Compress (slide 57)."""
        # round() is not what we want as round(0.5) == 0
        # int(0.5 + x) is what we want.
        return int(0.5 + self.r * 2**d / self.q) % 2**d

    @classmethod
    def decompress(cls, q, y, d):
        """Decompress (slide 57)."""
        # See comment on compress().
        return cls(int(0.5 + y * q / 2**d), q)


class KModPol(ModPol):
    """Element of R_q with Kyber extras."""

    coef_cls = KModInt

    @classmethod
    def rand_small_cbd(cls, q, n, eta):
        """Pick a small (size <= eta) element of R_q with CDB (slide 62)."""
        c = [cls.coef_cls.rand_small_cbd(q, eta) for _ in range(n)]
        return cls(q, n, c)

    @classmethod
    def from_seed(cls, q, n, B):
        """Generate pseudo-random element of R_q based on a seed."""
        # This is essentially Algorithm 7 SampleNTT from the spec.
        # The algorithm in the spec ouputs 256 elements in Z_q, which are
        # meant to be interpreted as a polynomial in the NTT domain.
        # Here we interpret them as a normal polynomial instead because we
        # haven't implemented NTT yet.
        #
        # We accept q and n as parameters but the algorithm only makes sense
        # if q has the expected bit length.
        if q.bit_length() != 12:
            raise NotImplementedError

        ctx = XOF()
        ctx.absorb(B)
        a = []
        while len(a) < n:
            C = ctx.squeeze(3)
            d1 = C[0] + 256 * (C[1] % 16)
            d2 = C[1] // 16 + 16 * C[2]
            if d1 < q:
                a.append(cls.coef_cls(d1, q))
            if d2 < q and len(a) < n:
                a.append(cls.coef_cls(d2, q))

        return cls(q, n, a)

    def to_bytes(self):
        """Serialize, based on ByteEncode_12 from the spec."""
        if self.q.bit_length() != 12 or self.n % 8 != 0:
            raise NotImplementedError

        out = bytes()
        for i in range(0, len(self.c), 2):
            c1, c2 = int(self.c[i]), int(self.c[i + 1])
            d1 = c1 % 256
            d2 = c1 // 256 + 16 * (c2 % 16)
            d3 = c2 // 16
            out += d1.to_bytes(1) + d2.to_bytes(1) + d3.to_bytes(1)

        return out

    def round(self):
        """Rounding (slide 47)."""
        return [a.round() for a in self.c]

    def compress(self, d):
        """Compress (slide 57)."""
        return [c.compress(d) for c in self.c]

    @classmethod
    def decompress(cls, q, n, c, d):
        """Decompress (slide 57)."""
        return cls(q, n, [cls.coef_cls.decompress(q, y, d) for y in c])


class KVec(Vec):
    """Element of R_q^k with Kyber extras."""

    item_cls = KModPol

    @classmethod
    def rand_small_cbd(cls, q, n, k, eta):
        """Pick a small (size <= eta) element of R_q^k with CBD (slide 62)."""
        v = [cls.item_cls.rand_small_cbd(q, n, eta) for _ in range(k)]
        return cls(v)

    def compress(self, d):
        """Compress (slide 57)."""
        return [x.compress(d) for x in self.v]

    @classmethod
    def decompress(cls, q, n, v, d):
        """Decompress (slide 57)."""
        return cls([cls.item_cls.decompress(q, n, c, d) for c in v])


class KMat(Mat):
    """Matrix of elements of R_q with Kyber extras."""

    line_cls = KVec
    item_cls = KModPol

    @classmethod
    def from_seed(cls, q, n, k, rho):
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
                a_ij = cls.item_cls.from_seed(q, n, B)
                a_i.append(a_ij)
            a.append(cls.line_cls(a_i))

        return cls(a)

    def to_bytes(self):
        """Serialize (line-wise)."""
        out = bytes()
        for line in self.lines:
            for x in line.v:
                out += x.to_bytes()

        return out
