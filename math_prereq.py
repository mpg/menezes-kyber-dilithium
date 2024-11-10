"""
Implement objects mentionned in V1b Mathematical Prerequisites.

This is an obvious implementation whose goal is to be readable.
When possible, the same notations as in the slides are used.

Not coded in a defensive way; for example all operations on Mod could raise
ValueError if the other value is not a Mod with the same modulus. I chose
not to clutter the code as this just a support for learning.

Things are naturally arranged in layers, each building on the previous one:
    1. ModInt: modular integers (slide 23)
    2. Pol: polynomial with ModInt coefficients (slide 24)
    3. ModPolGen: modular polynomials (slides 25-27)
    4. Vec: vectors of modular polynomials (slides 28-29)

There are at least two natural ways of constructing the modular polynomials
we'll need. The first, above, is the same as for modular integers; it's the
most generic and doesn't rely on the special form of the modulus. The second,
implemented in ModPol, fuses layers 2 and 3 above and takes advantage of the
special form of the modulus to combine multiplication with modular reduction.
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


class Mod:
    """Modular integer or polynomial (base class)."""

    def __init__(self, r, q):
        """Build r mod q."""
        self.r = r % q
        self.q = q

    def __repr__(self):
        """Represent self."""
        return f"{self.__class__.__name__}({self.r}, {self.q})"

    def __eq__(self, other):
        """Compare to another Mod."""
        return self.r == other.r and self.q == other.q

    def __add__(self, other):
        """Add another Mod."""
        return type(self)(self.r + other.r, self.q)

    def __sub__(self, other):
        """Subtract another Mod."""
        return type(self)(self.r - other.r, self.q)

    def __mul__(self, other):
        """Multiply by another Mod."""
        return type(self)(self.r * other.r, self.q)


class ModInt(Mod):
    """Modular integer (slide 23)."""

    def __int__(self):
        """Get the representative in [0, q)."""
        return self.r

    def size(self):
        """Size of self (slide 33)."""
        return min(self.r, self.q - self.r)

    def round(self):
        """Rounding (slide 47)."""
        return int(self.q / 4 <= self.r <= 3 * self.q / 4)

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


class Pol:
    """Polynomial with ModInt coefficients (slide 24)."""

    def __init__(self, q, c):
        """Build the polynomial c[0] + c[1] X + ... + c[n-1] X^n-1.

        The coefficients can be passed either as a list of ModInt
        or a list of integers."""
        if len(c) != 0 and not isinstance(c[0], ModInt):
            self.c = [ModInt(a, q) for a in c]
        else:
            self.c = c[:]
        self.q = q

        # Normalize: leading coefficient must not be 0.
        # (Convention: the 0 polynomial is represented with self.c == [].)
        while len(self.c) != 0 and self.c[-1] == ModInt(0, self.q):
            self.c.pop()

    def __repr__(self):
        """Represent self."""
        return f"Pol({self.q}, {self.c})"

    def __eq__(self, other):
        """Compare to another Pol."""
        return self.q == other.q and self.c == other.c

    def _c_padded(self, n):
        """Iterate over coefficients, padded with 0 until n elements have been
        returned."""
        for a in self.c:
            yield a
        for _ in range(n - len(self.c)):
            yield ModInt(0, self.q)

    def __add__(self, other):
        """Add another Pol."""
        n = max(len(self.c), len(other.c))
        c = [a + b for a, b in zip(self._c_padded(n), other._c_padded(n))]
        return Pol(self.q, c)

    def __sub__(self, other):
        """Subtract another Pol."""
        n = max(len(self.c), len(other.c))
        c = [a - b for a, b in zip(self._c_padded(n), other._c_padded(n))]
        return Pol(self.q, c)

    def __mul__(self, other):
        """Multiply by another Pol."""
        c = [ModInt(0, self.q)] * (len(self.c) + len(other.c))
        for i, a in enumerate(self.c):
            for j, b in enumerate(other.c):
                c[i + j] += a * b
        return Pol(self.q, c)

    def size(self):
        """Size of self (slide 33)."""
        return max((c.size() for c in self.c))

    def deg(self):
        """Degree of the polynomial."""
        # Note the degree of the 0 polynomial is undefined,
        # we chose to return -1 for simplicity's sake.
        return len(self.c) - 1

    def __mod__(self, other):
        """Remainder in the Euclidean division of self by other.

        This is the unique polynomial R such that:
        (1) self - R is a multiple of other, and
        (2) deg(R) < deg(other).

        For simplicity's sake, require other to be unitary (leading
        coefficient == 1), otherwise we'd need to implement division for
        ModInts, which is not hard but useless for our purposes.
        """
        if len(other.c) == 0:
            raise ZeroDivisionError
        if other.c[-1] != ModInt(1, self.q):
            raise NotImplementedError

        # We start with R == self and we'll subtract multiples of self;
        # that way (1) (from the dosctring) is a loop invariant.
        # At each iteration we cancel the leading term of R, decreasing its
        # degree; this is the loop variant, and (2) is the exit condition.
        r = Pol(self.q, self.c)
        while r.deg() >= other.deg():
            # Set f = a X^n where a is R's leading coefficient,
            # and n is such that f * other has the same degree as R.
            a = r.c[-1]
            n = r.deg() - other.deg()
            f = Pol(self.q, [ModInt(0, self.q)] * n + [a])

            r = r - f * other

        return r


# pylint: disable=too-few-public-methods
class ModPolGen(Mod):
    """Modular integer (slide 23)."""

    def size(self):
        """Size of self (slide 33)."""
        return self.r.size()


class ModPol:
    """Elements of R_q (slides 25-27), integrated implementation."""

    def __init__(self, q, n, c):
        """Build the polynomial c[0] + c[1] X + ... + c[n-1] X^n-1 mod X^n + 1.

        The coefficients can be passed either as a list of n ModInt
        or a list of n integers."""
        if len(c) != n or n == 0:
            raise ValueError

        if not isinstance(c[0], ModInt):
            self.c = [ModInt(a, q) for a in c]
        else:
            self.c = c[:]
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
                a.append(d1)
            if d2 < q and len(a) < n:
                a.append(d2)

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


class Vec:
    """Element of R_q^k, ie vector of ModPols (slide 28)."""

    def __init__(self, *v):
        """Build a vector given a list of k ModPols."""
        self.v = tuple(v)

    @classmethod
    def rand_uni(cls, q, n, k):
        """Pick an element of R_q^k uniformly at random."""
        v = [ModPol.rand_uni(q, n) for _ in range(k)]
        return cls(*v)

    @classmethod
    def rand_small_uni(cls, q, n, k, eta):
        """Pick a small (size <= eta) element of R_q^k uniformly at random."""
        v = [ModPol.rand_small_uni(q, n, eta) for _ in range(k)]
        return cls(*v)

    def __repr__(self):
        """Represent self."""
        return f"Vec({self.v})"

    def __eq__(self, other):
        """Compare to another Vec."""
        return self.v == other.v

    def __add__(self, other):
        """Add another Vec."""
        v = [a + b for a, b in zip(self.v, other.v)]
        return Vec(*v)

    def __sub__(self, other):
        """Subtract another Vec."""
        v = [a - b for a, b in zip(self.v, other.v)]
        return Vec(*v)

    def __mul__(self, other):
        """Inner product with another Vec; result is a ModPol (slide 28).
        Aka dot product or scalar product, denoted a^T b on later slides."""
        zero = self.v[0] - self.v[0]  # get the 0 ModPol(q, n)
        return sum((a * b for a, b in zip(self.v, other.v)), start=zero)

    def size(self):
        """Size of self (slide 33)."""
        return max((f.size() for f in self.v))


class Mat:
    """Matrix of elements of R_q."""

    def __init__(self, *lines):
        """Build a matrix given a list of lines (Vec)."""
        self.lines = tuple(lines)

    @classmethod
    def rand_uni(cls, q, n, k):
        """Pick an element of R_q^k*k uniformly at random."""
        lines = [Vec.rand_uni(q, n, k) for _ in range(k)]
        return cls(*lines)

    @classmethod
    def from_seed(cls, q, n, k, rho):
        """Generate pseudo-random square matrix based on a seed."""
        # This is lines 3-7 in Algorithm 13 K-PKE.KeyGen or equivalently
        # lines 4-8 in Algorithm 14 K-PKE.Encrypt in the standard,
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
            a.append(Vec(*a_i))

        return cls(*a)

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
        return Vec(*v)

    def transpose(self):
        """Return self's transpose."""
        m = [vec.v for vec in self.lines]
        t = [Vec(*[m[j][i] for j in range(len(m))]) for i in range(len(m[0]))]
        return Mat(*t)
