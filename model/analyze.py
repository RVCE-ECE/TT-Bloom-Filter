"""Characterise the hash functions and measure false-positive rates."""

import math
import random
from bloom import BloomFilter, h1, h2, M, K

print("=== Uniformity ===")
for name, fn in (("h1", h1), ("h2", h2)):
    counts = [0] * M
    for x in range(256):
        counts[fn(x)] += 1
    print(f"{name}: min={min(counts)} max={max(counts)} distinct={len(set(counts))}")

print("\n=== Independence ===")
same = sum(1 for x in range(256) if h1(x) == h2(x))
pairs = {(h1(x), h2(x)) for x in range(256)}
print(f"inputs where h1 == h2: {same} / 256")
print(f"distinct (h1,h2) pairs: {len(pairs)} / 256")

print("\n=== False positive rate ===")
print(f"{'n':>4} {'measured':>10} {'theory':>10}")
random.seed(1)
for n in (2, 4, 8, 12, 16, 20, 24, 32):
    trials, fp, total = 200, 0, 0
    for _ in range(trials):
        inserted = set(random.sample(range(256), n))
        b = BloomFilter()
        for v in inserted:
            b.insert(v)
        for x in range(256):
            if x not in inserted:
                total += 1
                fp += b.query(x)
    theory = (1 - math.exp(-K * n / M)) ** K
    print(f"{n:>4} {fp/total:>10.4f} {theory:>10.4f}")
