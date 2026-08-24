/*
 * Bloom filter control FSM.
 * Detects a rising edge on strobe, issues a single-cycle operation,
 * then pulses valid for one cycle.
 */
`default_nettype none

module bloom_ctrl (
    input  wire clk,
    input  wire rst_n,
    input  wire strobe,       // asynchronous-ish user input
    input  wire mode,         // 1 = insert, 0 = query
    input  wire hit,          // combinational result from the array
    output reg  do_insert,    // one-cycle pulse to the array
    output reg  valid,        // one-cycle pulse when result is ready
    output reg  result        // registered query answer
);

  localparam IDLE = 2'd0,
             EXEC = 2'd1,
             DONE = 2'd2;

  reg [1:0] state;
  reg       strobe_d;         // strobe delayed one cycle, for edge detect

  wire strobe_rise = strobe & ~strobe_d;

  always @(posedge clk) begin
    if (!rst_n) begin
      state     <= IDLE;
      strobe_d  <= 1'b0;
      do_insert <= 1'b0;
      valid     <= 1'b0;
      result    <= 1'b0;
    end else begin
      strobe_d  <= strobe;
      do_insert <= 1'b0;      // default: deassert unless set below
      valid     <= 1'b0;

      case (state)
        IDLE: begin
          if (strobe_rise) begin
            if (mode) do_insert <= 1'b1;   // insert: pulse the array
            else      result    <= hit;    // query: capture the answer
            state <= EXEC;
          end
        end

        EXEC: begin
          state <= DONE;
        end

        DONE: begin
          valid <= 1'b1;
          state <= IDLE;
        end

        default: state <= IDLE;
      endcase
    end
  end

endmodule
