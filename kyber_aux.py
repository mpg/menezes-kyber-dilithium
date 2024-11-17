"""
Auxiliary tools for Kyber.

These follow the spec¹ as they are omitted from the lectures
(see slide 78 "Omitted details").

¹ https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
"""

import hashlib


class XOF:
    """The XOF wrapper from the spec (4.1, pp. 19-20)."""

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
