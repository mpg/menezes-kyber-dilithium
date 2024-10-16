class ModInt:
    """Modular integer."""

    def __init__(self, r, q):
        """Build r mod q."""
        self.r = r % q
        self.q = q

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
