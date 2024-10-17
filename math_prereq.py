"""
Implement objects mentionned in V1b Mathematical Prerequisites.

This is an obvious implementation whose goal is to be readable.
When possible, the same notations as in the slides are used.

Not coded in a defensive way; for example all operations on Mod could raise
ValueError if the other value is not a Mod with the same modulus. I chose
not to clutter the code as this just a support for learning.

Things are naturally arranged in layers, each building on the previous one:
    1. Mod(int): modular integers (slide 23)
    2. Pol: polynomial with Mod(int) coefficients (slide 24)
    3. Mod(Pol): polynomial modulo X^n + 1 (slides 25-27)
    4. Vec: vectors of polynomials (slides 28-29)

There are at least two natural ways of constructing the modular polynomials
we'll need. The first, above, is the same as for modular integers; it's the
most generic and doesn't rely on the special form of the modulus. The second,
implemented in ModPol, fuses layers 2 and 3 above and takes advantage of the
special form of the modulus to combine multiplication with modular reduction.
"""


class Mod:
    """Modular integer (slide 23) or polynomial (slides 25-27)."""

    def __init__(self, r, q):
        """Build r mod q."""
        self.r = r % q
        self.q = q

    def __repr__(self):
        """Represent self."""
        return f"Mod({self.r}, {self.q})"

    def __eq__(self, other):
        """Compare to another Mod."""
        return self.r == other.r and self.q == other.q

    def __add__(self, other):
        """Add another Mod."""
        return Mod(self.r + other.r, self.q)

    def __sub__(self, other):
        """Subtract another Mod."""
        return Mod(self.r - other.r, self.q)

    def __mul__(self, other):
        """Multiply by another Mod."""
        return Mod(self.r * other.r, self.q)


class Pol:
    """Polynomial with Mod(int) coefficients (slide 24)."""

    def __init__(self, q, c):
        """Build the polynomial c[0] + c[1] X + ... + c[n-1] X^n-1.

        The coefficients can be passed either as a list of Mod(int)
        or a list of integers."""
        if len(c) != 0 and not isinstance(c[0], Mod):
            self.c = [Mod(a, q) for a in c]
        else:
            self.c = c[:]
        self.q = q

        # Normalize: leading coefficient must not be 0.
        # (Convention: the 0 polynomial is represented with self.c == [].)
        while len(self.c) != 0 and self.c[-1] == Mod(0, self.q):
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
            yield Mod(0, self.q)

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
        c = [Mod(0, self.q)] * (len(self.c) + len(other.c))
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
        Mod(int)s, which is not hard but useless for our purposes.
        """
        if len(other.c) == 0:
            raise ZeroDivisionError
        if other.c[-1] != Mod(1, self.q):
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
            f = Pol(self.q, [Mod(0, self.q)] * n + [a])

            r = r - f * other

        return r


class ModPol:
    """Elements of R_q (slides 25-27), integrated implementation."""

    def __init__(self, q, n, c):
        """Build the polynomial c[0] + c[1] X + ... + c[n-1] X^n-1 mod X^n + 1.

        The coefficients can be passed either as a list of n Mod(int)
        or a list of n integers."""
        if len(c) != n:
            raise ValueError

        if not isinstance(c[0], Mod):
            self.c = [Mod(a, q) for a in c]
        else:
            self.c = c[:]
        self.q = q
        self.n = n

    def __repr__(self):
        """Represent self."""
        return f"ModPol({self.q}, {self.n}, {self.c})"

    def __eq__(self, other):
        """Compare to another ModPol."""
        return self.q == other.q and self.n == other.n and self.c == other.c

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
        c = [Mod(0, self.q)] * self.n
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
