"""Compare the Verilog hash module against the Python golden model."""

import subprocess
import sys
from bloom import h1, h2

subprocess.run(
    ["iverilog", "-o", "/tmp/hash_dump", "hash_dump.v", "../src/hash.v"],
    check=True,
)
out = subprocess.run(["vvp", "/tmp/hash_dump"], capture_output=True, text=True).stdout

mismatches = 0
seen = 0
for line in out.strip().splitlines():
    parts = line.split()
    if len(parts) != 3:
        continue
    x, v1, v2 = (int(p) for p in parts)
    seen += 1
    if v1 != h1(x) or v2 != h2(x):
        mismatches += 1
        print(f"MISMATCH x={x}: rtl=({v1},{v2}) model=({h1(x)},{h2(x)})")

print(f"\nchecked {seen} inputs, {mismatches} mismatches")
sys.exit(1 if mismatches or seen != 256 else 0)
