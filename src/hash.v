/*
 * Bloom filter hash index generators.
 * Two XOR-fold hashes mapping an 8-bit value to a 6-bit array index.
 * Purely combinational: no clock, no state.
 */
`default_nettype none

module bloom_hash (
    input  wire [7:0] x,       // input value
    output wire [5:0] idx1,    // first hash index
    output wire [5:0] idx2     // second hash index
);

  // h1 = x[5:0] ^ {x[7:6], 4'b0000}
  assign idx1 = x[5:0] ^ {x[7:6], 4'b0000};

  // Rotate x left by 3: bit i moves to position i+3, top bits wrap to bottom.
  // Wiring only - zero gates.
  wire [7:0] r = {x[4:0], x[7:5]};

  // h2 = same fold applied to the rotated value
  assign idx2 = r[5:0] ^ {r[7:6], 4'b0000};

endmodule
