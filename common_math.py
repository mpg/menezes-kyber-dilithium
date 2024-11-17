"""
Implement objects mentionned in V1b Mathematical Prerequisites.

This is an obvious implementation whose goal is to be readable.
When possible, the same notations as in the slides are used.

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

import secrets


class ModInt:
    """Modular integer (slide 23)."""

    def __init__(self, r, q):
        """Build r mod q."""
        self.r = r % q
        self.q = q

    def __repr__(self):
        """Represent self."""
        return f"{type(self).__name__}({self.r}, {self.q})"

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


class ModPol:
    """Element of R_q (slides 25-27)."""

    coef_cls = ModInt

    def __init__(self, q, n, c):
        """Build c[0] + c[1] X + ... + c[n-1] X^n-1 mod X^n + 1."""
        if len(c) != n or n == 0 or not isinstance(c[0], self.coef_cls):
            raise ValueError

        self.c = tuple(c)
        self.q = q
        self.n = n

    @classmethod
    def rand_uni(cls, q, n):
        """Pick an element of R_q uniformly at random."""
        c = [cls.coef_cls.rand_uni(q) for _ in range(n)]
        return cls(q, n, c)

    @classmethod
    def rand_small_uni(cls, q, n, eta):
        """Pick a small (size <= eta) element of R_q uniformly at random."""
        c = [cls.coef_cls.rand_small_uni(q, eta) for _ in range(n)]
        return cls(q, n, c)

    def __repr__(self):
        """Represent self."""
        return f"type(self)({self.q}, {self.n}, {self.c})"

    def __eq__(self, other):
        """Compare to another ModPol."""
        # Comparison of q and n are implied by comparing coefficients
        return self.c == other.c

    def __add__(self, other):
        """Add another ModPol."""
        c = [a + b for a, b in zip(self.c, other.c)]
        # No need to reduce mod X^n + 1, the degree didn't increase
        return type(self)(self.q, self.n, c)

    def __sub__(self, other):
        """Subtract another ModPol."""
        c = [a - b for a, b in zip(self.c, other.c)]
        # No need to reduce mod X^n + 1, the degree didn't increase
        return type(self)(self.q, self.n, c)

    def __mul__(self, other):
        """Multiply by another ModPol."""
        c = [type(self).coef_cls(0, self.q)] * self.n
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
        return type(self)(self.q, self.n, c)

    def size(self):
        """Size of self (slide 33)."""
        return max((c.size() for c in self.c))


class Vec:
    """Element of R_q^k, ie vector of ModPols (slide 28)."""

    item_cls = ModPol

    def __init__(self, v):
        """Build a vector given a list of k ModPols."""
        if len(v) == 0 or not isinstance(v[0], self.item_cls):
            raise ValueError

        self.v = tuple(v)

    @classmethod
    def rand_uni(cls, q, n, k):
        """Pick an element of R_q^k uniformly at random."""
        v = [cls.item_cls.rand_uni(q, n) for _ in range(k)]
        return cls(v)

    @classmethod
    def rand_small_uni(cls, q, n, k, eta):
        """Pick a small (size <= eta) element of R_q^k uniformly at random."""
        v = [cls.item_cls.rand_small_uni(q, n, eta) for _ in range(k)]
        return cls(v)

    def __repr__(self):
        """Represent self."""
        return f"{type(self).__name__}({self.v})"

    def __eq__(self, other):
        """Compare to another Vec."""
        return self.v == other.v

    def __add__(self, other):
        """Add another Vec."""
        v = [a + b for a, b in zip(self.v, other.v)]
        return type(self)(v)

    def __sub__(self, other):
        """Subtract another Vec."""
        v = [a - b for a, b in zip(self.v, other.v)]
        return type(self)(v)

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

    item_cls = ModPol
    line_cls = Vec

    def __init__(self, lines):
        """Build a matrix given a list of lines (Vec)."""
        if len(lines) == 0 or not isinstance(lines[0], self.line_cls):
            raise ValueError

        self.lines = tuple(lines)

    @classmethod
    def rand_uni(cls, q, n, k):
        """Pick an element of R_q^k*k uniformly at random."""
        lines = [cls.line_cls.rand_uni(q, n, k) for _ in range(k)]
        return cls(lines)

    def __repr__(self):
        """Represent self."""
        return f"{type(self).__name__}({self.lines})"

    def __eq__(self, other):
        """Compare to another Mat."""
        return self.lines == other.lines

    def __matmul__(self, vec):
        """Multiply by a Vec."""
        v = [l * vec for l in self.lines]
        return self.line_cls(v)

    def transpose(self):
        """Return self's transpose."""
        m = [vec.v for vec in self.lines]
        t = [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]
        return type(self)([self.line_cls(l) for l in t])
