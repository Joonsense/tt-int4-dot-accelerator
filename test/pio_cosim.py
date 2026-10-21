# chip-lab S5: 데모보드 PIO 호스트(host/pio_stream.py)를 PIO 에뮬레이터(pio_emu.py)로 돌리며 RTL 과 핀 단위로 함께 시뮬레이션한다.
# 시스템 클록마다 SM0·SM1 한 명령 → 핀을 칩에 → 칩 출력을 2클록 동기화기로 PIO 에. 칩 클록은 SM0 의 side-set 이 만든다.
# 확인하는 것: 같은 PioDot API(load·batch·batch_dot·stream·long_dot) 결과가 파이썬 정수 계산과 같고, 칩 클록당 시스템 클록 수.
import json
import os
import random
import sys

import cocotb
from cocotb.task import bridge, resume
from cocotb.triggers import Timer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "host"))
sys.path.insert(0, HERE)
import pio_emu  # noqa: E402
from test import N, WIDTH  # noqa: E402

try:
    from test import INT4
except ImportError:
    INT4 = False
try:
    from test import OPS as _program  # noqa: F401
    STATIONARY = True
except ImportError:
    STATIONARY = False

HOST = pio_emu.load_host_pio(os.path.join(HERE, "..", "host", "pio_stream.py"))
SYS_MHZ = 150


class EmuBackend:
    def __init__(self, dut):
        self.dut = dut
        self.gpio = pio_emu.Gpio()
        self.irq = [0] * 8
        self.sm0 = pio_emu.StateMachine(HOST.feeder, self.gpio, self.irq, out_base=HOST.UI_BASE, sideset_base=HOST.CLK_PIN, jmp_pin=HOST.IN_READY_PIN)
        self.sm1 = pio_emu.StateMachine(HOST.capture, self.gpio, self.irq, in_base=HOST.UO_BASE, jmp_pin=HOST.OUT_VALID_PIN)
        self.load = 0
        self.sys_cycles = self.chip_clocks = 0
        self.last_clk = 0

    def set_load(self, value):
        self.load = 1 if value else 0

    @resume
    async def cycle(self):
        self.sm0.step()
        self.sm1.step()
        level = self.gpio.level
        ui = sum(level.get(HOST.UI_BASE + i, 0) << i for i in range(8))
        uio = sum(level.get(HOST.UIO_BASE + i, 0) << i for i in range(4)) | (self.load << 6)
        self.dut.ui_in.value = ui
        self.dut.uio_in.value = uio
        clk = level.get(HOST.CLK_PIN, 0)
        self.dut.clk.value = clk
        await Timer(1, unit="ns")
        if clk and not self.last_clk:
            self.chip_clocks += 1
        self.last_clk = clk
        uio_out = self.dut.uio_out.value.to_unsigned()
        uo = self.dut.uo_out.value.to_unsigned()
        outputs = {HOST.IN_READY_PIN: (uio_out >> 4) & 1, HOST.OUT_VALID_PIN: (uio_out >> 5) & 1}
        outputs.update({HOST.UO_BASE + i: (uo >> i) & 1 for i in range(8)})
        self.gpio.clock(outputs)
        self.sys_cycles += 1

    def run(self, stream, count):
        got, index, guard = [], 0, 0
        while index < len(stream) or len(got) < count or self.sm0.tx:
            while index < len(stream) and len(self.sm0.tx) < 4:   # DMA 가 FIFO 를 늘 채운다고 가정
                self.sm0.tx.append(stream[index])
                index += 1
            self.cycle()
            while self.sm1.rx:
                got.append(self.sm1.rx.pop(0) & 255)
            guard += 1
            if guard > 400 * (len(stream) + 10):
                raise RuntimeError(f"PIO 진행 없음: 단어 {index}/{len(stream)}, 결과 {len(got)}/{count}")
        return got[:count]


async def reset(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    for _ in range(5):
        dut.clk.value = 0
        await Timer(5, unit="ns")
        dut.clk.value = 1
        await Timer(5, unit="ns")
    dut.rst_n.value = 1
    dut.clk.value = 0
    await Timer(5, unit="ns")


def rand(rng, length):
    low, high = (-8, 7) if INT4 else (-128, 127)
    return [rng.randint(low, high) for _ in range(length)]


@cocotb.test()
async def test_pio_host_against_rtl(dut):
    await reset(dut)
    backend = EmuBackend(dut)
    chip = HOST.PioDot(N, WIDTH, int4=INT4, stationary=STATIONARY, backend=backend)
    rng = random.Random(7)
    lim = (1 << (WIDTH - 1)) - 1
    sat = lambda v: max(-lim - 1, min(lim, v))
    m = chip.base.elements
    if STATIONARY:
        w = rand(rng, m)
        xs = [rand(rng, m) for _ in range(40)]
        await bridge(chip.load)(w)
        start_sys, start_chip = backend.sys_cycles, backend.chip_clocks
        got = await bridge(chip.batch)(xs)
        steady = (backend.sys_cycles - start_sys, backend.chip_clocks - start_chip, len(xs) * m)
        assert got == [sat(sum(a * b for a, b in zip(w, x))) for x in xs]
        long_w, long_xs = rand(rng, 100), [rand(rng, 100) for _ in range(3)]
        assert await bridge(chip.batch_dot)(long_w, long_xs) == [sum(a * b for a, b in zip(long_w, x)) for x in long_xs]
    else:
        vectors = [(rand(rng, m), rand(rng, m)) for _ in range(40)]
        start_sys, start_chip = backend.sys_cycles, backend.chip_clocks
        got = await bridge(chip.stream)(vectors)
        steady = (backend.sys_cycles - start_sys, backend.chip_clocks - start_chip, len(vectors) * m)
        assert got == [sat(sum(a * b for a, b in zip(a_, b_))) for a_, b_ in vectors]
    sys_cycles, chip_clocks, macs = steady
    per_clock = sys_cycles / chip_clocks
    summary = {'sys_cycles_per_chip_clock': round(per_clock, 2), 'chip_mhz_at_150mhz_sys': round(SYS_MHZ / per_clock, 2),
               'macs': macs, 'chip_clocks': chip_clocks, 'mmac_per_s_at_150mhz_sys': round(macs / sys_cycles * SYS_MHZ, 2),
               'int4': INT4, 'stationary': STATIONARY}
    dut._log.info('PIO ' + json.dumps(summary))
    with open('pio_result.json', 'w') as handle:
        json.dump(summary, handle)
