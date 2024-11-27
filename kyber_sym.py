"""
Symmetric crypto for Kyber.

This will be section 4.1 from the spec¹: cryptographic functions.
¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

These are omitted from the lectures (see slide 78 "Omitted details").
"""

import hashlib


class XOF:
    """The XOF wrapper from the spec (sec. 4.1, pp. 19-20)."""

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


class PRF:  # pylint: disable=too-few-public-methods
    """The PRF from the spec (sec. 4.1, p. 18), stateful version."""

    # In the spec, callers have to maintain a counter and pass it
    # on each call as well as the seed. Here we hold these internally.
    def __init__(self, seed):
        """Create a new stateful PRF."""
        self.s = seed
        self.b = 0

    def next(self, eta):
        """Return PRF_eta(s, b) and update b."""
        ctx = hashlib.shake_256(self.s + self.b.to_bytes(1))
        self.b += 1
        return ctx.digest(64 * eta)  # size in bytes (the spec has bits)


def G(c):
    """The G function from the spec: section 4.1, page 19, (4.5)."""
    # Also split the output in two, see the text above (4.5)
    g = hashlib.sha3_512(c).digest()
    return g[:32], g[32:]


def H(s):
    """The H function from the spec: section 4.1, page 18, (4.4)."""
    return hashlib.sha3_256(s).digest()


def J(s):
    """The J function from the spec: section 4.1, page 18, (4.4)."""
    return hashlib.shake_256(s).digest(32)  # size in bytes (the spec has bits)
