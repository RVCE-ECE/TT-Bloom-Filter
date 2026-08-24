/*
 * Bloom Filter Membership Tester - Tiny Tapeout
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none

module tt_um_manasvibhat_bloom_filter (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

  localparam M     = 64;
  localparam IDX_W = 6;

  wire [IDX_W-1:0] idx1, idx2;
  wire             hit;
  wire             do_insert, valid, result;

  wire mode    = uio_in[0];   // 1 = insert, 0 = query
  wire strobe  = uio_in[1];
  wire dbg_sel = uio_in[2];

  bloom_hash u_hash (
      .x    (ui_in),
      .idx1 (idx1),
      .idx2 (idx2)
  );

  bloom_array #(
      .M     (M),
      .IDX_W (IDX_W)
  ) u_array (
      .clk       (clk),
      .rst_n     (rst_n),
      .idx1      (idx1),
      .idx2      (idx2),
      .do_insert (do_insert),
      .hit       (hit)
  );

  bloom_ctrl u_ctrl (
      .clk       (clk),
      .rst_n     (rst_n),
      .strobe    (strobe),
      .mode      (mode),
      .hit       (hit),
      .do_insert (do_insert),
      .valid     (valid),
      .result    (result)
  );

  wire [IDX_W-1:0] dbg_idx = dbg_sel ? idx2 : idx1;

  assign uo_out  = {dbg_idx, valid, result};
  assign uio_out = 8'h00;
  assign uio_oe  = 8'h00;

  wire _unused = &{ena, uio_in[7:3], 1'b0};

endmodule
