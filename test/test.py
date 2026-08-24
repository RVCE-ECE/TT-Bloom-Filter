# SPDX-License-Identifier: Apache-2.0
"""Testbench for the Bloom filter membership tester."""

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

from bloom_model import BloomFilter, M, K

INSERT = 1
QUERY = 0


async def reset(dut):
    """Reset the DUT and clear the bit array."""
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


def uio(mode=0, strobe=0, dbg_sel=0):
    """Pack the control bits into the uio_in byte."""
    return (dbg_sel << 2) | (strobe << 1) | mode


async def operation(dut, value, mode):
    """Drive one insert or query and wait for the valid handshake.

    Returns the RESULT bit (uo_out[0]), meaningful only for queries.
    """
    dut.ui_in.value = value
    dut.uio_in.value = uio(mode=mode, strobe=0)
    await ClockCycles(dut.clk, 1)

    # Rising edge on strobe starts the operation
    dut.uio_in.value = uio(mode=mode, strobe=1)

    # Wait for VALID (uo_out[1]) with a timeout so a hang fails loudly
    for _ in range(20):
        await RisingEdge(dut.clk)
        if (int(dut.uo_out.value) >> 1) & 1:
            break
    else:
        raise AssertionError(f"VALID never asserted for value={value:#04x}")

    result = int(dut.uo_out.value) & 1

    # Drop the strobe so the next rising edge is detectable
    dut.uio_in.value = uio(mode=mode, strobe=0)
    await ClockCycles(dut.clk, 2)
    return result


async def insert(dut, value):
    await operation(dut, value, INSERT)


async def query(dut, value):
    return await operation(dut, value, QUERY)


@cocotb.test()
async def test_reset_clears_array(dut):
    """After reset, nothing is a member."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    await reset(dut)

    for value in (0x00, 0x10, 0x7F, 0xFF):
        assert await query(dut, value) == 0, f"{value:#04x} present after reset"

    dut._log.info("Reset clears the array: PASS")


@cocotb.test()
async def test_no_false_negatives(dut):
    """Every inserted value must query back as 1. This is the core guarantee."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    await reset(dut)

    inserted = [0x10, 0x25, 0x7F, 0xA3, 0x01, 0xFE]
    for value in inserted:
        await insert(dut, value)

    for value in inserted:
        assert await query(dut, value) == 1, (
            f"FALSE NEGATIVE on {value:#04x} - design fault"
        )

    dut._log.info(f"No false negatives across {len(inserted)} values: PASS")


@cocotb.test()
async def test_exhaustive_against_model(dut):
    """Sweep all 256 inputs and compare bit-for-bit with the golden model."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    await reset(dut)

    random.seed(7)
    inserted = sorted(random.sample(range(256), 12))

    model = BloomFilter()
    for value in inserted:
        await insert(dut, value)
        model.insert(value)

    mismatches = 0
    false_negatives = 0
    false_positives = 0

    for value in range(256):
        rtl = await query(dut, value)
        ref = model.query(value)

        if rtl != ref:
            mismatches += 1
            dut._log.error(f"MISMATCH {value:#04x}: rtl={rtl} model={ref}")

        if value in inserted and rtl == 0:
            false_negatives += 1
        if value not in inserted and rtl == 1:
            false_positives += 1

    negatives = 256 - len(inserted)
    rate = false_positives / negatives

    dut._log.info(f"inserted n={len(inserted)}, m={M}, k={K}")
    dut._log.info(f"false negatives: {false_negatives}")
    dut._log.info(f"false positives: {false_positives}/{negatives} = {rate:.4f}")

    assert mismatches == 0, f"{mismatches} RTL/model mismatches"
    assert false_negatives == 0, "FALSE NEGATIVE - design fault"

    dut._log.info("Exhaustive 256-value check: PASS")
