"""Golden reference model for the Tiny Tapeout Bloom filter.

Mirrors the hardware exactly. Used as the reference in cocotb tests
and to measure false-positive rates before committing to RTL.
"""

M = 64   # bit array size
K = 2    # number of hash functions


def h1(x):
    """First hash: fold bits 7:6 down onto bits 5:4."""
    x &= 0xFF
    return (x & 0x3F) ^ ((x >> 6) << 4)


def h2(x):
    """Second hash: rotate left by 3, then the same fold."""
    x &= 0xFF
    r = ((x << 3) | (x >> 5)) & 0xFF
    return (r & 0x3F) ^ ((r >> 6) << 4)


class BloomFilter:
    def __init__(self):
        self.bits = 0          # M-bit array as a Python integer

    def reset(self):
        self.bits = 0

    def insert(self, x):
        self.bits |= (1 << h1(x)) | (1 << h2(x))

    def query(self, x):
        a = (self.bits >> h1(x)) & 1
        b = (self.bits >> h2(x)) & 1
        return a & b
