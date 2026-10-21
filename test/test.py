# SPDX-License-Identifier: Apache-2.0
# chip-lab 내보내기: 기대값은 chip-lab 고정 기준 모델(reference-1.0, seed 42)에서 계산했다.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, Timer


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

N = 8
INTERVAL = 8
INT4 = True
NBYTES = 3
WIDTH = 20
OPS = [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [136, 0, 0], [136, 0, 0], [136, 0, 0], [136, 0, 0], [136, 0, 0], [136, 0, 0], [136, 0, 0], [136, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [135, 1, 0], [135, 1, 0], [135, 1, 0], [135, 1, 0], [135, 1, 0], [135, 1, 0], [135, 1, 0], [135, 1, 0], [17, 0, 0], [17, 0, 0], [17, 0, 0], [17, 0, 0], [17, 0, 0], [17, 0, 0], [17, 0, 0], [17, 0, 0], [245, 0, 0], [6, 0, 0], [216, 0, 0], [37, 0, 0], [192, 0, 0], [46, 0, 0], [171, 0, 0], [180, 0, 0], [191, 0, 0], [4, 0, 0], [54, 0, 0], [61, 0, 0], [227, 0, 0], [160, 0, 0], [253, 0, 0], [109, 0, 0], [198, 0, 0], [192, 0, 0], [15, 0, 0], [69, 0, 0], [243, 0, 0], [124, 0, 0], [154, 0, 0], [203, 0, 0], [93, 1, 0], [74, 1, 0], [100, 1, 0], [128, 1, 0], [11, 1, 0], [178, 1, 0], [81, 1, 0], [109, 1, 0], [8, 0, 0], [189, 0, 0], [225, 0, 0], [60, 0, 0], [141, 0, 0], [114, 0, 0], [184, 0, 0], [19, 0, 0], [52, 0, 0], [102, 0, 0], [251, 0, 0], [175, 0, 0], [130, 0, 0], [255, 0, 0], [168, 0, 0], [249, 0, 0], [53, 0, 0], [85, 0, 0], [150, 0, 0], [155, 0, 0], [36, 0, 0], [251, 0, 0], [238, 0, 0], [198, 0, 0], [78, 0, 0], [217, 0, 0], [132, 0, 0], [4, 0, 0], [22, 0, 0], [117, 0, 0], [236, 0, 0], [225, 0, 0], [153, 1, 0], [146, 1, 0], [121, 1, 0], [157, 1, 0], [218, 1, 0], [170, 1, 0], [79, 1, 0], [251, 1, 0], [169, 0, 0], [37, 0, 0], [224, 0, 0], [242, 0, 0], [64, 0, 0], [28, 0, 0], [38, 0, 0], [138, 0, 0], [203, 0, 0], [176, 0, 0], [203, 0, 0], [16, 0, 0], [46, 0, 0], [14, 0, 0], [7, 0, 0], [169, 0, 0], [92, 0, 0], [156, 0, 0], [49, 0, 0], [57, 0, 0], [254, 0, 0], [59, 0, 0], [197, 0, 0], [223, 0, 0], [19, 0, 0], [255, 0, 0], [232, 0, 0], [36, 0, 0], [160, 0, 0], [48, 0, 0], [36, 0, 0], [184, 0, 0], [208, 1, 0], [144, 1, 0], [91, 1, 0], [35, 1, 0], [181, 1, 0], [228, 1, 0], [144, 1, 0], [133, 1, 0], [62, 0, 0], [165, 0, 0], [34, 0, 0], [27, 0, 0], [81, 0, 0], [66, 0, 0], [193, 0, 0], [94, 0, 0], [26, 0, 0], [162, 0, 0], [31, 0, 0], [239, 0, 0], [140, 0, 0], [249, 0, 0], [167, 0, 0], [86, 0, 0], [108, 0, 0], [98, 0, 0], [101, 0, 0], [125, 0, 0], [6, 0, 0], [15, 0, 0], [247, 0, 0], [96, 0, 0], [98, 0, 0], [149, 0, 0], [94, 0, 0], [132, 0, 0], [116, 0, 0], [56, 0, 0], [65, 0, 0], [245, 0, 0], [247, 1, 0], [80, 1, 0], [135, 1, 0], [36, 1, 0], [212, 1, 0], [198, 1, 0], [72, 1, 0], [168, 1, 0], [197, 0, 0], [214, 0, 0], [9, 0, 0], [36, 0, 0], [110, 0, 0], [34, 0, 0], [4, 0, 0], [5, 0, 0], [235, 0, 0], [6, 0, 0], [211, 0, 0], [219, 0, 0], [177, 0, 0], [24, 0, 0], [68, 0, 0], [174, 0, 0], [198, 0, 0], [213, 0, 0], [112, 0, 0], [86, 0, 0], [32, 0, 0], [175, 0, 0], [96, 0, 0], [111, 0, 0], [95, 0, 0], [247, 0, 0], [119, 0, 0], [134, 0, 0], [26, 0, 0], [79, 0, 0], [31, 0, 0], [115, 0, 0], [83, 1, 0], [50, 1, 0], [6, 1, 0], [1, 1, 0], [191, 1, 0], [46, 1, 0], [219, 1, 0], [238, 1, 0], [7, 0, 0], [177, 0, 0], [30, 0, 0], [63, 0, 0], [29, 0, 0], [200, 0, 0], [144, 0, 0], [25, 0, 0], [167, 0, 0], [201, 0, 0], [28, 0, 0], [250, 0, 0], [91, 0, 0], [79, 0, 0], [102, 0, 0], [81, 0, 0], [145, 0, 0], [31, 0, 0], [97, 0, 0], [250, 0, 0], [224, 0, 0], [181, 0, 0], [207, 0, 0], [192, 0, 0], [2, 0, 0], [168, 0, 0], [143, 0, 0], [144, 0, 0], [125, 0, 0], [6, 0, 0], [93, 0, 0], [167, 0, 0], [55, 1, 0], [37, 1, 0], [178, 1, 0], [45, 1, 0], [117, 1, 0], [65, 1, 0], [105, 1, 0], [42, 1, 0], [32, 0, 0], [75, 0, 0], [104, 0, 0], [149, 0, 0], [62, 0, 0], [103, 0, 0], [233, 0, 0], [192, 0, 0], [110, 1, 0], [55, 1, 0], [134, 1, 0], [217, 1, 0], [195, 1, 0], [144, 1, 0], [157, 1, 0], [243, 1, 0], [230, 0, 1], [207, 0, 1], [60, 0, 1], [66, 0, 1], [41, 0, 1], [192, 0, 1], [90, 0, 1], [100, 0, 1], [207, 0, 1], [105, 0, 1], [247, 0, 1], [243, 0, 1], [172, 0, 1], [185, 0, 1], [121, 0, 1], [36, 0, 1], [240, 0, 0], [73, 0, 0], [197, 0, 0], [237, 0, 0], [50, 0, 0], [126, 0, 0], [127, 0, 0], [211, 0, 0], [119, 1, 0], [119, 1, 0], [119, 1, 0], [119, 1, 0], [119, 1, 0], [119, 1, 0], [119, 1, 0], [119, 1, 0], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 1], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [119, 0, 0], [231, 1, 0], [177, 1, 0], [165, 1, 0], [68, 1, 0], [26, 1, 0], [76, 1, 0], [111, 1, 0], [31, 1, 0], [239, 0, 0], [119, 0, 0], [245, 0, 0], [237, 0, 0], [194, 0, 0], [13, 0, 0], [38, 0, 0], [181, 0, 0], [248, 1, 0], [74, 1, 0], [3, 1, 0], [14, 1, 0], [39, 1, 0], [221, 1, 0], [163, 1, 0], [73, 1, 0], [133, 0, 1], [101, 0, 1], [199, 0, 1], [228, 0, 1], [147, 0, 1], [15, 0, 1], [133, 0, 1], [130, 0, 1], [2, 0, 0], [74, 0, 0], [153, 0, 0], [73, 0, 0], [121, 0, 0], [60, 0, 0], [75, 0, 0], [133, 0, 0]]
WANT = [0, 0, 0, 0, -8, 155, 37, 58, -62, -17, -51, -60, 120, 150, 62, 42, -22, 68, -65, 14, -99, -11, 17, -119, 34, -135, -16, -80, -15, -164, 3920, -28, -107]
IN_VALID, OUT_READY, CHAIN, LOAD = 1, 4, 8, 64


def pin(dut, bit):
    return (dut.uio_out.value.to_unsigned() >> bit) & 1


def signed(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value >> (bits - 1) else value


async def collect(dut, got, done_at):
    raw, count, cycle = 0, 0, 0
    while True:
        await FallingEdge(dut.clk)
        cycle += 1
        if pin(dut, 5):
            raw |= dut.uo_out.value.to_unsigned() << (8 * count)
            count += 1
            if count == NBYTES:
                got.append(signed(raw, WIDTH))
                done_at.append(cycle)
                raw, count = 0, 0


async def drive(dut, ops):
    index = 0
    while index < len(ops):
        data, load, chain = ops[index]
        dut.ui_in.value = data & 0xFF
        dut.uio_in.value = IN_VALID | OUT_READY | (LOAD if load else 0) | (CHAIN if chain else 0)
        await Timer(1, unit="us")
        ready = pin(dut, 4)
        await FallingEdge(dut.clk)
        if ready:
            index += 1
    dut.uio_in.value = OUT_READY


@cocotb.test()
async def test_weight_stationary_program(dut):
    await reset(dut)
    await FallingEdge(dut.clk)
    got, done_at = [], []
    cocotb.start_soon(collect(dut, got, done_at))
    await drive(dut, OPS)
    for _ in range(4 * NBYTES + 12):
        await FallingEdge(dut.clk)
    assert got == WANT, f"{got} != {WANT}"
    # 쉼 없는 간격: 같은 가중치로 x 벡터 4개를 연달아 → 결과 간격 = INTERVAL (x 바이트 N 개 = MAC 2·N 회)
    got.clear(); done_at.clear()
    xs = [op for op in OPS if not op[1]][:4 * N]
    await drive(dut, [(op[0], 0, 0) for op in xs])
    for _ in range(4 * NBYTES + 12):
        await FallingEdge(dut.clk)
    gaps = {b - a for a, b in zip(done_at, done_at[1:])}
    assert gaps == {INTERVAL}, f"벡터 간격 {gaps} (기대 {INTERVAL})"


import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "host"))
import pin_client  # noqa: E402
from cocotb.task import bridge, resume  # noqa: E402


class CocotbPort:
    def __init__(self, dut):
        self.dut = dut

    @resume
    async def write(self, data, control):
        self.dut.ui_in.value = data
        self.dut.uio_in.value = control

    @resume
    async def read(self):
        await Timer(1, unit="us")
        return self.dut.uio_out.value.to_unsigned(), self.dut.uo_out.value.to_unsigned()

    @resume
    async def tick(self):
        await FallingEdge(self.dut.clk)


def rand(rng, length):
    low, high = (-8, 7) if INT4 else (-128, 127)
    return [rng.randint(low, high) for _ in range(length)]


@cocotb.test()
async def test_host_batch(dut):
    await reset(dut)
    await FallingEdge(dut.clk)
    chip = pin_client.PinDot(CocotbPort(dut), N, WIDTH, int4=INT4, stationary=True)
    rng = random.Random(42)
    lim = (1 << (WIDTH - 1)) - 1
    for _ in range(3):
        w = rand(rng, chip.elements)
        xs = [rand(rng, chip.elements) for _ in range(20)]
        await bridge(chip.load)(w)
        got = await bridge(chip.batch)(xs)
        assert got == [max(-lim - 1, min(lim, sum(a * b for a, b in zip(w, x)))) for x in xs]


@cocotb.test()
async def test_host_batch_dot_long(dut):
    await reset(dut)
    await FallingEdge(dut.clk)
    chip = pin_client.PinDot(CocotbPort(dut), N, WIDTH, int4=INT4, stationary=True)
    rng = random.Random(43)
    for length in (100, 784):
        w = rand(rng, length)
        xs = [rand(rng, length) for _ in range(5)]
        got = await bridge(chip.batch_dot)(w, xs)
        assert got == [sum(a * b for a, b in zip(w, x)) for x in xs], f"길이 {length}"
