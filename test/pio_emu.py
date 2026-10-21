"""RP2040/RP2350 PIO 의 작은 부분집합 에뮬레이터 (chip-lab 자체 제작, 2026-10-22).

host_pio.py 의 @rp2.asm_pio 함수를 **그대로** 실행해 명령을 모은다 (가짜 rp2 모듈을 끼워 넣는다).
지원: pull(block) · out(pins,n) · in_(pins,n) · push(block) · irq(n) · wait(1, irq, n) · jmp(label) · jmp(pin, label)
· nop · .side(v) · [delay] · label · wrap_target/wrap. 상태 기계는 한 시스템 클록에 명령 하나 (지연은 추가 클록).
GPIO 입력은 2클록 동기화기를 거친다 (실제 PIO 입력 동기화와 같은 지연을 가정). 하드웨어 동작의 근사이며 실기 검증이 아니다.
"""
import sys
import types


class Instr:
    def __init__(self, op, *args):
        self.op, self.args, self.side_value, self.delay = op, args, None, 0

    def side(self, value):
        self.side_value = value
        return self

    def __getitem__(self, delay):
        self.delay = delay
        return self


class Program:
    def __init__(self, function, options):
        self.options = options
        self.instrs, self.labels, self.wrap_target, self.wrap = [], {}, 0, None
        names = {}

        def emit(op):
            def make(*args):
                instr = Instr(op, *args)
                self.instrs.append(instr)
                return instr
            return make

        for op in ('pull', 'out', 'in_', 'push', 'irq', 'wait', 'jmp', 'nop'):
            names[op] = emit(op)
        names['label'] = lambda name: self.labels.__setitem__(name, len(self.instrs))
        names['wrap_target'] = lambda: setattr(self, 'wrap_target', len(self.instrs))
        names['wrap'] = lambda: setattr(self, 'wrap', len(self.instrs) - 1)
        names.update(block='block', noblock='noblock', pins='pins', pin='pin')   # irq 는 명령이자 wait 의 출처 표시 (MicroPython 과 같다)
        globals_ = dict(function.__globals__)
        globals_.update(names)
        types.FunctionType(function.__code__, globals_)()
        if self.wrap is None:
            self.wrap = len(self.instrs) - 1
        bad = [name for name, at in self.labels.items() if at >= len(self.instrs)]
        if bad:   # 실제 PIO 에서도 프로그램 밖 주소다
            raise ValueError(f'프로그램 끝을 가리키는 label: {bad}')


def fake_rp2():
    """host_pio.py 를 CPython 에서 import 할 수 있게 하는 가짜 rp2 (asm_pio 는 Program 을 만든다)."""
    rp2 = types.ModuleType('rp2')
    pio = types.SimpleNamespace(OUT_LOW=0, OUT_HIGH=1, SHIFT_LEFT='left', SHIFT_RIGHT='right')
    rp2.PIO = pio
    rp2.asm_pio = lambda **options: (lambda function: Program(function, options))
    rp2.StateMachine = None
    return rp2


def load_host_pio(path):
    """host_pio.py (내보낸 host/pio_stream.py) 를 가짜 rp2 로 불러온다."""
    sys.modules['rp2'] = fake_rp2()
    namespace = {'__name__': 'pio_stream'}
    exec(compile(open(path).read(), str(path), 'exec'), namespace)
    return types.SimpleNamespace(**{k: v for k, v in namespace.items() if not k.startswith('__')})


class StateMachine:
    def __init__(self, program, gpio, irq, out_base=None, in_base=None, sideset_base=None, jmp_pin=None):
        self.p, self.gpio, self.irq = program, gpio, irq
        self.out_base, self.in_base, self.sideset_base, self.jmp_pin = out_base, in_base, sideset_base, jmp_pin
        self.pc, self.osr, self.osr_count, self.isr, self.stall = 0, 0, 0, 0, 0
        self.tx, self.rx = [], []
        self.right = program.options.get('out_shiftdir', 'right') == 'right'

    def step(self):
        if self.stall:
            self.stall -= 1
            return
        instr = self.p.instrs[self.pc]
        done, jump = True, None
        op, args = instr.op, instr.args
        if op == 'pull':
            if self.tx:
                self.osr, self.osr_count = self.tx.pop(0), 32
            elif args and args[0] == 'block':
                done = False
        elif op == 'out':
            count = args[1]
            value = self.osr & ((1 << count) - 1)
            self.osr >>= count
            for i in range(count):
                self.gpio.drive(self.out_base + i, (value >> i) & 1)
        elif op == 'in_':
            count = args[1]
            value = sum(self.gpio.read(self.in_base + i) << i for i in range(count))
            self.isr = ((self.isr << count) | value) & 0xFFFFFFFF
        elif op == 'push':
            if len(self.rx) >= 4:
                done = not (args and args[0] == 'block')
            else:
                self.rx.append(self.isr)
                self.isr = 0
        elif op == 'irq':
            self.irq[args[0]] = 1
        elif op == 'wait':
            polarity, source, index = args
            if self.irq[index] == polarity:
                self.irq[index] = 0
            else:
                done = False
        elif op == 'jmp':
            if len(args) == 2:
                if self.gpio.read(self.jmp_pin):
                    jump = self.p.labels[args[1]]
            else:
                jump = self.p.labels[args[0]]
        if instr.side_value is not None:
            self.gpio.drive(self.sideset_base, instr.side_value)
        if not done:
            return
        self.stall = instr.delay
        if jump is not None:
            self.pc = jump
        elif self.pc == self.p.wrap:
            self.pc = self.p.wrap_target
        else:
            self.pc += 1


class Gpio:
    """출력 값은 즉시, 입력 읽기는 2클록 전 값 (동기화기)."""

    def __init__(self):
        self.level = {}
        self.history = [{}, {}]

    def drive(self, pin, value):
        self.level[pin] = value

    def read(self, pin):
        return self.history[0].get(pin, 0)

    def clock(self, chip_outputs):
        self.level.update(chip_outputs)
        self.history = [self.history[1], dict(self.level)]
