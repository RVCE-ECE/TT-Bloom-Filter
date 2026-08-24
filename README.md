# Bloom Filter Membership Tester

A hardware Bloom filter implemented as a Tiny Tapeout ASIC on the SkyWater
130nm process (shuttle TTSKY26C).

Submitted by Manasvi Bhat K, Vaishnavi Karpur and Shylashree N,
RV College of Engineering.

## What it does

A Bloom filter is a probabilistic data structure for set membership testing.
It answers "have I seen this value before?" using far less memory than
storing the values themselves, at the cost of an asymmetric guarantee: a
negative answer is always correct, but a positive answer may be wrong.
It never produces a false negative; it can produce a false positive.

This implementation uses a 64-bit array and two hash functions over 8-bit
input values. Insert sets two bits derived from the input; query returns
whether both of those bits are already set.

## Design

| | |
|---|---|
| Bit array | 64 bits (64 flip-flops) |
| Hash functions | 2, XOR-fold, 4 gates total |
| Input width | 8 bits |
| Control | 3-state FSM with strobe edge detection |
| Latency | 3 clock cycles from strobe to VALID |
| Target clock | 10 MHz |

The hash functions are deliberately non-cryptographic. A Bloom filter only
requires reasonably uniform, mutually independent hashes; it does not need
collision resistance. XOR-folds satisfy this at negligible area cost, which
is what allows the design to fit in a single tile.

## Results

**Hash quality.** Both hash functions are perfectly uniform — every one of
the 64 indices has exactly four preimages among the 256 possible inputs.
The pair map `x -> (h1(x), h2(x))` is injective: all 256 inputs produce a
distinct index pair, so no two values ever write the same two bits.

**Verification.** Exhaustive simulation over all 256 possible inputs, at
both RTL and gate level, against a Python golden model. Zero mismatches,
zero false negatives.

**False positive rate.** With 12 values inserted: 17 false positives out of
244 non-members, a rate of 0.070. Theory predicts 0.098 for m=64, k=2, n=12.
The measured rate is lower, consistent with the injectivity property, which
the standard formula does not model.

**Implementation.** 660 standard cells at 38.4% tile utilisation in sky130A,
including 71 flip-flops (64 array bits plus 7 for control). 21647 um of
routing.

## Interface

| Pin | Function |
|---|---|
| `ui_in[7:0]` | Input value |
| `uio_in[0]` | Mode: 1 = insert, 0 = query |
| `uio_in[1]` | Strobe (rising edge starts an operation) |
| `uio_in[2]` | Debug select: 0 = show h1, 1 = show h2 |
| `uo_out[0]` | Result: 1 = possibly present, 0 = definitely absent |
| `uo_out[1]` | Valid (one-cycle pulse) |
| `uo_out[7:2]` | Selected hash index |

Full operating instructions are in [docs/info.md](docs/info.md).

## Repository layout

    src/          RTL: top level, hash, bit array, control FSM
    test/         cocotb testbench and golden model
    model/        Python reference model and analysis scripts
    docs/info.md  Project datasheet

## Running the tests

    cd test
    pip install -r requirements.txt
    make -B

## License

Apache 2.0. See [LICENSE](LICENSE).
