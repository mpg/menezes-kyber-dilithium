"""
Implement objects mentionned in V1b Mathematical Prerequisites.

This is an obvious implementation whose goal is to be readable.
When possible, the same notations as in the slides are used.

Not coded in a defensive way; for example all operations on ModInt could raise
ValueError if the other value is not a ModInt with the same modulus. I chose
not to clutter the code as this just a support for learning.

Things are naturally arranged in layers, each building on the previous one:
    1. ModInt: modular integers (slide 23)
    2. Pol: polynomial with ModInt coefficients (slide 24)
    3. ModPol: polynomial modulo X^n + 1 (slides 25-27)
    4. Vec: vectors of polynomials (slides 28-29)
"""


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
        return ModInt(self.r + other.r, self.q)

    def __sub__(self, other):
        """Subtract another ModInt."""
        return ModInt(self.r - other.r, self.q)

    def __mul__(self, other):
        """Multiply by another ModInt."""
        return ModInt(self.r * other.r, self.q)


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
            print("R", r)
            # Set f = a X^n where a is R's leading coefficient,
            # and n is such that f * other has the same degree as R.
            a = r.c[-1]
            n = r.deg() - other.deg()
            f = Pol(self.q, [ModInt(0, self.q)] * n + [a])
            print("f", f)

            r = r - f * other

        print("R", r)
        return r
