"""
Implement objects mentionned in V1b Mathematical Prerequisites,
as well Kyber methods for these objects (such as pseudo-random generation).

This is an obvious implementation whose goal is to be readable.
When possible, the same notations as in the slides are used.
(Or as in the spec¹ when the dosctring or comment mentions the spec.)
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

Not coded in a defensive way; for example all operations on ModInt could raise
ValueError if the other value is not a ModInt with the same modulus. I chose
not to clutter the code as this just a support for learning.

Things are naturally arranged in layers, each building on the previous one:
    1. ModInt: modular integers (slide 23)
    2. ModPol: modular polynomials (slides 24-27)
    3. Vec: vectors of modular polynomials (slides 28-29)
    4. Mat: matrices of modular polynomials (slides 38-40)

There are at least two natural ways of constructing the modular polynomials
we'll need. The first is the same as for modular integers : we first construst
polynomials, with euclidean division (aka modulo) and then implement modular
polynomials based on that. The second, implemented in ModPol, fuses those two
steps above and takes advantage of the special form of the modulus to combine
multiplication with modular reduction. An implementation based on the first,
more generic approach can be found in previous commits.
"""

import hashlib
import secrets


class XOF:
    """The XOF wrapper from the spec."""

    def __init__(self):
        """Create a new XOF context."""
        self.ctx = hashlib.shake_128()
        # The hashlib API doesn't have a streaming squeeze() API
        # so we'll emulate it using digest() and an offset.
        self.offset = 0

    def absorb(self, data):
        """Absorb data."""
        self.ctx.update(data)
        self.offset = 0

    def squeeze(self, l):
        """Squeeze the next l bytes out."""
        # This is very inefficient but it works.
        out = self.ctx.digest(self.offset + l)[self.offset :]
        self.offset += l
        return out


class ModInt:
    """Modular integer (slide 23)."""

    def __init__(self, r, q):
        """Build r mod q."""
        self.r = r % q
        self.q = q

    def __repr__(self):
        """Represent self."""
        return f"ModInt({self.r}, {self.q})"

    def __eq__(self, other):
        """Compare to another ModInt."""
        return self.r == other.r and self.q == other.q

    def __add__(self, other):
        """Add another ModInt."""
        return type(self)(self.r + other.r, self.q)

    def __sub__(self, other):
        """Subtract another ModInt."""
        return type(self)(self.r - other.r, self.q)

    def __mul__(self, other):
        """Multiply by another ModInt."""
        return type(self)(self.r * other.r, self.q)

    def __int__(self):
        """Get the representative in [0, q)."""
        return self.r

    def size(self):
        """Size of self (slide 33)."""
        return min(self.r, self.q - self.r)

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

    @classmethod
    def rand_uni(cls, q):
        """Pick a ModInt uniformly at random."""
        return cls(secrets.randbelow(q), q)

    @classmethod
    def rand_small_uni(cls, q, eta):
        """Pick a small (size <= eta) ModInt uniformly at random."""
        pos = secrets.randbelow(2 * eta + 1)  # [0, 2*eta]
        sym = pos - eta  # [-eta, eta]
        return cls(sym, q)

    @classmethod
    def rand_small_cbd(cls, q, eta):
        """Pick a small (size <= eta) ModInt with central binomial
        distribution (slide 62)."""
        a = [secrets.randbits(1) for _ in range(eta)]
        b = [secrets.randbits(1) for _ in range(eta)]
        c = sum(ai - bi for ai, bi in zip(a, b))
        return cls(c, q)


class ModPol:
    """Elements of R_q (slides 25-27), integrated implementation."""

    def __init__(self, q, n, c):
        """Build c[0] + c[1] X + ... + c[n-1] X^n-1 mod X^n + 1."""
        if len(c) != n or n == 0:
            raise ValueError

        self.c = tuple(c)
        self.q = q
        self.n = n

    @classmethod
    def rand_uni(cls, q, n):
        """Pick an element of R_q uniformly at random."""
        c = [ModInt.rand_uni(q) for _ in range(n)]
        return cls(q, n, c)

    @classmethod
    def rand_small_uni(cls, q, n, eta):
        """Pick a small (size <= eta) element of R_q uniformly at random."""
        c = [ModInt.rand_small_uni(q, eta) for _ in range(n)]
        return cls(q, n, c)

    @classmethod
    def rand_small_cbd(cls, q, n, eta):
        """Pick a small (size <= eta) element of R_q with CDB (slide 62)."""
        c = [ModInt.rand_small_cbd(q, eta) for _ in range(n)]
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
                a.append(ModInt(d1, q))
            if d2 < q and len(a) < n:
                a.append(ModInt(d2, q))

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

    def __repr__(self):
        """Represent self."""
        return f"ModPol({self.q}, {self.n}, {self.c})"

    def __eq__(self, other):
        """Compare to another ModPol."""
        # Comparison of q and n are implied by comparing coefficients
        return self.c == other.c

    def __add__(self, other):
        """Add another ModPol."""
        c = [a + b for a, b in zip(self.c, other.c)]
        # No need to reduce mod X^n + 1, the degree didn't increase
        return ModPol(self.q, self.n, c)

    def __sub__(self, other):
        """Subtract another ModPol."""
        c = [a - b for a, b in zip(self.c, other.c)]
        # No need to reduce mod X^n + 1, the degree didn't increase
        return ModPol(self.q, self.n, c)

    def __mul__(self, other):
        """Multiply by another ModPol."""
        c = [ModInt(0, self.q)] * self.n
        for i, a in enumerate(self.c):
            for j, b in enumerate(other.c):
                p = a * b
                k = i + j
                # Immediately reduce mod X^n + 1: if we would add p*X^k,
                # then instead subtract p*X^{k-n} since mod X^n + 1 we have:
                #   X^n + 1 == 0
                #   X^n == -1
                #   X^n * X^{k-n} == -1 * X^{k-n}
                #   X^k == - X^{k-n}
                # (that's the 4th bullet on slide 26).
                if k >= self.n:
                    c[k - self.n] -= p
                else:
                    c[k] += p
        return ModPol(self.q, self.n, c)

    def size(self):
        """Size of self (slide 33)."""
        return max((c.size() for c in self.c))

    def round(self):
        """Rounding (slide 47)."""
        return [a.round() for a in self.c]

    def compress(self, d):
        """Compress (slide 57)."""
        return [c.compress(d) for c in self.c]

    @classmethod
    def decompress(cls, q, n, c, d):
        """Decompress (slide 57)."""
        return cls(q, n, [ModInt.decompress(q, y, d) for y in c])


class Vec:
    """Element of R_q^k, ie vector of ModPols (slide 28)."""

    def __init__(self, v):
        """Build a vector given a list of k ModPols."""
        self.v = tuple(v)

    @classmethod
    def rand_uni(cls, q, n, k):
        """Pick an element of R_q^k uniformly at random."""
        v = [ModPol.rand_uni(q, n) for _ in range(k)]
        return cls(v)

    @classmethod
    def rand_small_uni(cls, q, n, k, eta):
        """Pick a small (size <= eta) element of R_q^k uniformly at random."""
        v = [ModPol.rand_small_uni(q, n, eta) for _ in range(k)]
        return cls(v)

    @classmethod
    def rand_small_cbd(cls, q, n, k, eta):
        """Pick a small (size <= eta) element of R_q^k with CBD (slide 62)."""
        v = [ModPol.rand_small_cbd(q, n, eta) for _ in range(k)]
        return cls(v)

    def __repr__(self):
        """Represent self."""
        return f"Vec({self.v})"

    def __eq__(self, other):
        """Compare to another Vec."""
        return self.v == other.v

    def __add__(self, other):
        """Add another Vec."""
        v = [a + b for a, b in zip(self.v, other.v)]
        return Vec(v)

    def __sub__(self, other):
        """Subtract another Vec."""
        v = [a - b for a, b in zip(self.v, other.v)]
        return Vec(v)

    def __mul__(self, other):
        """Inner product with another Vec; result is a ModPol (slide 28).
        Aka dot product or scalar product, denoted a^T b on later slides."""
        zero = self.v[0] - self.v[0]  # get the 0 ModPol(q, n)
        return sum((a * b for a, b in zip(self.v, other.v)), start=zero)

    def size(self):
        """Size of self (slide 33)."""
        return max((f.size() for f in self.v))

    def compress(self, d):
        """Compress (slide 57)."""
        return [x.compress(d) for x in self.v]

    @classmethod
    def decompress(cls, q, n, v, d):
        """Decompress (slide 57)."""
        return cls([ModPol.decompress(q, n, c, d) for c in v])


class Mat:
    """Matrix of elements of R_q."""

    def __init__(self, lines):
        """Build a matrix given a list of lines (Vec)."""
        self.lines = tuple(lines)

    @classmethod
    def rand_uni(cls, q, n, k):
        """Pick an element of R_q^k*k uniformly at random."""
        lines = [Vec.rand_uni(q, n, k) for _ in range(k)]
        return cls(lines)

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
                a_ij = ModPol.from_seed(q, n, B)
                a_i.append(a_ij)
            a.append(Vec(a_i))

        return cls(a)

    def to_bytes(self):
        """Serialize (line-wise)."""
        out = bytes()
        for line in self.lines:
            for x in line.v:
                out += x.to_bytes()

        return out

    def __repr__(self):
        """Represent self."""
        return f"Mat({self.lines})"

    def __eq__(self, other):
        """Compare to another Mat."""
        return self.lines == other.lines

    def __matmul__(self, vec):
        """Multiply by a Vec."""
        v = [l * vec for l in self.lines]
        return Vec(v)

    def transpose(self):
        """Return self's transpose."""
        m = [vec.v for vec in self.lines]
        t = [Vec([m[j][i] for j in range(len(m))]) for i in range(len(m[0]))]
        return Mat(t)
