// Standalone harness: prints h1,h2 for all 256 inputs.
// Not part of the chip - a verification aid only.
`timescale 1ns/1ps
`default_nettype none

module hash_dump;
  reg  [7:0] x;
  wire [5:0] idx1, idx2;
  integer i;

  bloom_hash dut (.x(x), .idx1(idx1), .idx2(idx2));

  initial begin
    for (i = 0; i < 256; i = i + 1) begin
      x = i[7:0];
      #1;                                    // let combinational logic settle
      $display("%0d %0d %0d", x, idx1, idx2);
    end
    $finish;
  end
endmodule
