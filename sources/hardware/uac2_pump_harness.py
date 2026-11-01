#!/usr/bin/env python3
"""Execute the original MX-1 Thumb audio pump under explicitly mocked MMIO.

This is a control-flow experiment, not an ESC2 USB peripheral emulator and
not a successful physical USB audio test. Original instructions are executed;
the optional variant changes only the OUT-dependent startup boolean.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SHA256 = '256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b'
PUMP = 0x01009840
RETURN = 0x0100f680
PATCH = 0x01009a06
USBF = 0x40010000
OUT_STATUS = USBF + 0x16c
IN_STATUS = USBF + 0x174
OUT_FIFO = USBF + 0x1f4
IN_FIFO = USBF + 0x1b8
PHASE_SOURCE = 0x40003228
STATE = 0x01010048
DSP_CAPTURE = 0x40101048
CONVERT_INT = 0x4004056c
CONVERT_FLOAT = 0x40040574


def word(n):
    return struct.pack('<I', n)


def run_case(blob, mapping, patched, scenario, stereo=False,
             out_stereo=None, in_stereo=None):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for base, size in ((0x01000000, 0x20000), (0x20000000, 0x20000),
                       (0x40000000, 0x50000), (0x40100000, 0x20000)):
        uc.mem_map(base, size)
    for operation in mapping['operations']:
        if operation['kind'] != 'copy' or not operation['length']:
            continue
        address = operation['destination']
        if 0x01000000 <= address < 0x01020000 or 0x20000000 <= address < 0x20020000:
            offset = operation['source'] - 0x60000000
            uc.mem_write(address, blob[offset:offset + operation['length']])
    assert bytes(uc.mem_read(PATCH, 4)) == bytes.fromhex('4f f0 00 0c')
    if patched:
        uc.mem_write(PATCH, bytes.fromhex('4f f0 01 0c'))

    # Unique nonzero values exercise the real audio-data arm after priming.
    # Conversion is an identity mock: real ESC2 fixed/float scaling is unknown.
    for channel in range(18):
        uc.mem_write(DSP_CAPTURE + channel * 4, word(0x11000000 + channel * 0x100))
    out_stereo = stereo if out_stereo is None else out_stereo
    in_stereo = stereo if in_stereo is None else in_stereo
    uc.mem_write(USBF + 0x17c,
                 word(((2 if out_stereo else 1) << 16) |
                      ((2 if in_stereo else 1) << 12)))
    uc.mem_write(USBF + 0xd8, word(112 if out_stereo else 1008))

    sample = 0
    fifo_writes = []
    commits = []
    controls = []
    out_reads = []
    state_history = []

    def read_hook(engine, access, address, size, value, user):
        if address == OUT_FIFO:
            out_reads.append(sample)
            # Silence on playback makes the native duplex comparison stable.
            engine.mem_write(address, word(0))

    def write_hook(engine, access, address, size, value, user):
        if address == IN_FIFO:
            fifo_writes.append((sample, value))
        elif address == IN_STATUS:
            commits.append((sample, value))
        elif address == USBF + 0x170:
            controls.append((sample, value))
        elif address == CONVERT_FLOAT:
            engine.mem_write(CONVERT_INT, word(value))
        elif address == CONVERT_INT:
            engine.mem_write(CONVERT_FLOAT, word(value))

    uc.hook_add(UC_HOOK_MEM_READ, read_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)

    # Ninety audio ticks with one rising phase edge every six ticks. This is
    # an explicit 48-kHz-like stimulus; the hardware phase source is not emulated.
    for sample in range(90):
        active = scenario != 'stop_restart' or sample < 36 or sample >= 54
        out_ready = scenario == 'duplex' or (scenario == 'playback_then_silent' and sample < 24)
        uc.mem_write(PHASE_SOURCE, word(2 if sample % 6 < 3 else 0))
        uc.mem_write(OUT_STATUS, word(8 if out_ready else 0))
        # Explicitly assume host IN readiness: bits16,24 and FIFO-ready bit2.
        uc.mem_write(IN_STATUS, word(0x01010004 if active else 0))
        uc.reg_write(UC_ARM_REG_SP, 0x2001ff00)
        uc.reg_write(UC_ARM_REG_LR, RETURN | 1)
        uc.emu_start(PUMP | 1, RETURN, count=10000)
        assert uc.reg_read(UC_ARM_REG_PC) == RETURN, 'pump did not return'
        state_history.append(struct.unpack('<I', uc.mem_read(STATE, 4))[0])

    return {
        'scenario': scenario,
        'patched': patched,
        'stereo': stereo,
        'out_stereo': out_stereo,
        'in_stereo': in_stereo,
        'capture_fifo_word_count': len(fifo_writes),
        'first_capture_fifo_tick': fifo_writes[0][0] if fifo_writes else None,
        'first_nonzero_capture_tick': next((t for t, v in fifo_writes if v), None),
        'commit_count': len(commits),
        'first_commit_tick': commits[0][0] if commits else None,
        'endpoint_reset_count': len(controls),
        'out_fifo_word_read_count': len(out_reads),
        'max_capture_state': max(state_history),
        'state_history': state_history,
        # Detailed records support differential checks, omitted from final JSON.
        '_fifo_writes': fifo_writes,
        '_commits': commits,
        '_controls': controls,
        '_out_reads': out_reads,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'sources/hardware/uac2_pump_harness_results.json')
    args = parser.parse_args()
    blob = (ROOT / 'analysis/container_app_main.bin').read_bytes()
    assert hashlib.sha256(blob).hexdigest() == EXPECTED_SHA256
    mapping = json.loads((ROOT / 'analysis/map-main.json').read_text())

    results = []
    for scenario in ('capture_only', 'duplex', 'stop_restart', 'playback_then_silent'):
        original = run_case(blob, mapping, False, scenario)
        patched = run_case(blob, mapping, True, scenario)
        results.extend((original, patched))
        if scenario in ('capture_only', 'stop_restart'):
            assert original['capture_fifo_word_count'] == 0
            assert original['max_capture_state'] == 1
            assert patched['capture_fifo_word_count'] > 0
            assert patched['out_fifo_word_read_count'] == 0
            assert patched['max_capture_state'] == 4
            assert patched['first_capture_fifo_tick'] < patched['first_nonzero_capture_tick']
            first_nonzero = patched['first_nonzero_capture_tick']
            assert all(v == 0 for t, v in patched['_fifo_writes'] if t < first_nonzero)
            if scenario == 'stop_restart':
                assert not any(36 <= t < 54 for t, v in patched['_fifo_writes'])
                assert any(t >= 54 for t, v in patched['_fifo_writes'])
        if scenario in ('duplex', 'playback_then_silent'):
            # The original and variant must be identical when startup already
            # had playback. Capture state4 already survives later OUT silence.
            for key in ('_fifo_writes', '_commits', '_controls', 'state_history', '_out_reads'):
                assert original[key] == patched[key], (scenario, key)
            assert original['capture_fifo_word_count'] > 0
            if scenario == 'playback_then_silent':
                assert any(t >= 24 for t, v in original['_fifo_writes'])

    stereo = run_case(blob, mapping, True, 'capture_only', True)
    results.append(stereo)
    assert stereo['out_fifo_word_read_count'] == 0
    assert stereo['max_capture_state'] == 4
    per_tick = {}
    for tick, value in stereo['_fifo_writes']:
        per_tick[tick] = per_tick.get(tick, 0) + 1
    assert set(per_tick.values()) == {2}

    # The host may select different AS alternatives for the two directions.
    # These cases exercise the independent channel branches only; the model
    # does not certify packet-tail accounting or real FIFO byte counts.
    for out_stereo, in_stereo in ((False, True), (True, False)):
        original = run_case(blob, mapping, False, 'duplex',
                            out_stereo=out_stereo, in_stereo=in_stereo)
        patched = run_case(blob, mapping, True, 'duplex',
                           out_stereo=out_stereo, in_stereo=in_stereo)
        for key in ('_fifo_writes', '_commits', '_controls', 'state_history', '_out_reads'):
            assert original[key] == patched[key]
        per_tick = {}
        for tick, value in patched['_fifo_writes']:
            per_tick[tick] = per_tick.get(tick, 0) + 1
        assert set(per_tick.values()) == {2 if in_stereo else 18}
        if out_stereo:
            counts = {}
            for tick in patched['_out_reads']:
                counts[tick] = counts.get(tick, 0) + 1
            assert set(counts.values()) == {2}
        results.extend((original, patched))

    report = {
        'schema': 'mx1-original-audio-pump-mocked-mmio-v1',
        'status': 'PASS: actual Thumb control flow under a deliberately limited MMIO model',
        'hardware_verified': False,
        'input_main_sha256': EXPECTED_SHA256,
        'function_runtime': hex(PUMP),
        'function_bytes': 732,
        'patch_runtime': hex(PATCH),
        'patch_image_offset': hex(mapping['operations'][0]['source'] - 0x60000000 +
                                  PATCH - mapping['operations'][0]['destination']),
        'before_hex': '4f f0 00 0c',
        'after_hex': '4f f0 01 0c',
        'modeled_assumptions': [
            'IN status bits16,24,2 are externally supplied as ready while host capture is active.',
            'USB clock/phase register bit1 follows an externally supplied six-tick periodic sequence.',
            'OUT readiness bit3 is externally supplied; capture-only cases keep it zero throughout.',
            'Integer/float conversion registers use an identity mock; numeric audio correctness is not tested.',
            'FIFO capacity, bus tokens, NAK/underrun behavior, real DMA timing, and hardware reset effects are not modeled.',
        ],
        'demonstrated': [
            'Original capture-only code remains in state1 and writes no IN FIFO data under these inputs.',
            'The one-instruction variant primes IN with silence and reaches normal capture state4 with no OUT reads.',
            'Original and variant traces match for duplex startup and for capture continuing after playback stops.',
            'The variant stops and restarts capture when modeled IN readiness is removed and restored.',
            'The original stereo-alt2 arm writes two capture words per audio tick under the same variant.',
            'Mixed OUT18/IN2 and OUT2/IN18 cases exercise independent alternate-selection branches with unchanged duplex traces.',
        ],
        'cases': [{k: v for k, v in result.items() if not k.startswith('_')} for result in results],
    }
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])
    for result in results:
        print(f"{result['scenario']:20s} patched={result['patched']} "
              f"OUT_channels={2 if result['out_stereo'] else 18} "
              f"IN_channels={2 if result['in_stereo'] else 18} "
              f"IN_words={result['capture_fifo_word_count']} OUT_reads={result['out_fifo_word_read_count']} "
              f"max_state={result['max_capture_state']}")
    print(args.output)


if __name__ == '__main__':
    main()
