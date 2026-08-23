/*
 * Bloom filter bit array with insert and query paths.
 * M bits of storage, addressed by two independent indices.
 */
`default_nettype none

module bloom_array #(
    parameter M     = 64,   // array size in bits
    parameter IDX_W = 6     // log2(M)
) (
    input  wire             clk,
    input  wire             rst_n,     // active low, clears the array
    input  wire [IDX_W-1:0] idx1,
    input  wire [IDX_W-1:0] idx2,
    input  wire             do_insert, // 1 for one cycle to set both bits
    output wire             hit        // combinational: both bits currently set
);

  reg [M-1:0] bits;

  // Query path: read both addressed bits and AND them.
  // Synthesis builds two M-to-1 multiplexers here.
  assign hit = bits[idx1] & bits[idx2];

  // Insert path: set both addressed bits. Bits are never cleared
  // except by reset - this monotonicity is why false negatives
  // are structurally impossible.
  always @(posedge clk) begin
    if (!rst_n)
      bits <= {M{1'b0}};
    else if (do_insert)
      bits <= bits | ({{(M-1){1'b0}}, 1'b1} << idx1)
                   | ({{(M-1){1'b0}}, 1'b1} << idx2);
  end

endmodule
