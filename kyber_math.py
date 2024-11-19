"""
Extends mathematical objects (from V1b) with Kyber speficic methods.

Some methods follow the lectures, and mention a slide number.
Some methods follow the actual ML-KEM spec¹ and mention it.
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
"""

from common_math import ModInt, ModPol, Vec, Mat

from kyber_aux import XOF, bits_from_bytes

# Currently we're in a transitional state because some method take q, n as
# arguments, and some use the global constants; so we need disting names.
# When all methods have test cases with the appropriate size, we can make all
# methods use the global constants instead.
#
# Common to all Kyber sizes.
Q = 3329
N = 256


class KModInt(ModInt):
    """Modular integer with Kyber extras."""

    @classmethod
    def cbd_from_bits(cls, eta, bits):
        """Small (size <= eta) modular integer with CBD from bits."""
        # This is lines 3, 4 and 5 (rhs) of Algorithm 8 SamplePolyCBD
        r = sum(bits[:eta]) - sum(bits[eta:])
        return cls(r, Q)

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
        return cls(Q, N, c)

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
    def cbd_from_prf(cls, k, eta, prf):
        """Generate a pseudo-random CBD small vector from a PRF."""
        # This is the loops in Algorithm 13 lines 8-11 and 12-15
        # and Algorithm 14 lines 9-12 and 13-16.
        v = [cls.item_cls.cbd_from_prf(eta, prf) for _ in range(k)]
        return cls(v)

    def compress(self, d):
        """Compress (slide 57)."""
        return [x.compress(d) for x in self.v]

    def to_bytes(self):
        """Serialize."""
        return b"".join((x.to_bytes() for x in self.v))

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
