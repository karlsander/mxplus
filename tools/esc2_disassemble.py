#!/usr/bin/env python3
"""Lossless, partial ESC2 packet disassembly and stock effect relocation audit.

The low-five-bit framing rule and possible flow targets are inferred from the
stock corpus, not an ISA manual. Unknown operations retain their raw encoding.
This tool neither patches firmware nor executes DSP arithmetic.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/esc2-disassembly'


@dataclass(frozen=True)
class Packet:
    offset: int
    words: tuple[int, ...]
    kind: str = 'packet'

    def encode(self):
        return struct.pack('>' + 'H' * len(self.words), *self.words)


def decode(data: bytes, offset: int, *, gate=False, trailer=False) -> list[Packet]:
    """Parse one bounded upload chunk; never scan ahead to resynchronize.

Special words are accepted only when explicitly requested by the corpus map.
They are retained as opaque records, without invented instruction semantics.
    """
    if offset < 0 or offset % 2 or len(data) % 2:
        raise ValueError('Unaligned program interval')
    records = []
    pos = 0
    if gate:
        if offset != 0 or data[:4] != b'\x00\x00\x00\x01':
            raise ValueError('Unexpected stock gate words')
        records.append(Packet(offset, (0, 1), 'gate_words'))
        pos = 4
    limit = len(data)
    if trailer:
        if limit - pos < 2 or data[-2:] != b'\0\0':
            raise ValueError('Unexpected stock terminal word')
        limit -= 2
    while pos < limit:
        header = int.from_bytes(data[pos:pos + 2], 'big')
        length = header & 31
        if length == 0 or pos + length * 2 > limit:
            raise ValueError(f'Invalid/truncated packet at {offset + pos:#x}: {header:04x}')
        words = struct.unpack_from('>' + 'H' * length, data, pos)
        records.append(Packet(offset + pos, words))
        pos += length * 2
    if trailer:
        records.append(Packet(offset + limit, (0,), 'terminal_word'))
    if b''.join(p.encode() for p in records) != data:
        raise AssertionError('Disassembly did not round trip')
    return records


def logical_image(cpu_image):
    if len(cpu_image) % 4:
        raise ValueError('CPU program image is not word aligned')
    return b''.join(struct.pack('>I', word) for (word,) in struct.iter_unpack('<I', cpu_image))


def flow_target(packet):
    # An inference: root-program fields land on independently uploaded chunk
    # entrances. Factory terminal targets are retained even though not packets.
    if packet.kind == 'packet' and packet.words[0] == 0x0b03:
        return packet.words[2] * 2
    return None


def binding_tail(packet):
    """Recognize a conservative operand-selector pattern, not an ISA decode.

The last contiguous group of xfeN words precedes a literal tail. Low five bits
index bytes within that tail. Reject groups that cannot satisfy that model.
Direction, arithmetic, width and pipeline latency remain unknown here.
    """
    words = packet.words
    if packet.kind != 'packet':
        return []
    runs = []
    i = 1
    while i < len(words):
        if words[i] & 0x0fe0 != 0x0fe0:
            i += 1
            continue
        start = i
        while i < len(words) and words[i] & 0x0fe0 == 0x0fe0:
            i += 1
        positions = [words[j] & 31 for j in range(start, i)]
        if (positions == sorted(set(positions)) and
                all(p % 2 == 0 and i + p // 2 < len(words) for p in positions)):
            runs.append([(j, i + (words[j] & 31) // 2) for j in range(start, i)])
    return runs[0] if len(runs) == 1 else []


def listing_line(packet, labels=None):
    raw = ' '.join(f'{x:04x}' for x in packet.words)
    note = packet.kind
    if packet.kind == 'packet':
        note = f'packet[{len(packet.words)}]'
        target = flow_target(packet)
        if target is not None:
            note += f' flow? mode={packet.words[1]:04x} target={target:04x}'
        bindings = binding_tail(packet)
        if bindings:
            note += ' bindings? ' + ','.join(
                f'{packet.words[i]:04x}->{packet.words[j]:04x}@{packet.offset + j * 2:04x}'
                for i, j in bindings)
            if labels:
                names = [labels[packet.words[j]] for _, j in bindings if packet.words[j] in labels]
                if names:
                    note += ' coefficient refs? ' + ', '.join(names)
    return f'{packet.offset:04x}: {raw:<84} ; {note}'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit_mixer_controls(blob):
    from fx_sends_audit import SendMachine, callback_registry

    machine = SendMachine(blob)
    registry = callback_registry(blob)
    controls = []
    labels = {}
    specifications = []
    for channel in range(11):
        specifications.extend([
            (0x125 + channel, [1 + channel, 12 + channel], (0, 64, 127)),
            (0x130 + channel, [45 + channel], (0, 64, 127)),
            (0x15c + channel, [67 + channel], (0, 1)),
            (0x167 + channel, [56 + channel], (0, 64, 127)),
        ])
    specifications.extend([(0xae, [79], (0, 64, 127)), (0xaf, [78], (0, 64, 127))])
    for parameter, indices, values in specifications:
        pointer = struct.unpack_from('<I', blob, 0x6f278 + 4 * parameter)[0]
        name = blob[pointer - 0x60000000:].split(b'\0', 1)[0].decode('ascii')
        callback, _ = registry[parameter]
        cases = []
        for value in values:
            requests = machine.checked(callback, 0, value)
            assert [r['index'] for r in requests] == indices
            assert all(r['kind'] == 'coefficient' and r['core'] == 1 for r in requests)
            assert machine.writes
            cases.append({'value': value, 'requests': requests})
        for index in indices:
            assert 0xc000 + index not in labels
            labels[0xc000 + index] = name
        controls.append({'parameter_id': parameter, 'name': name,
                         'callback_runtime': hex(callback),
                         'callback_decoded_offset': hex(callback - 0x60000000), 'cases': cases})
    return controls, labels


def audit_contexts(blob):
    from fx_sends_audit import SendMachine
    from unicorn.arm_const import UC_ARM_REG_R2, UC_ARM_REG_R3

    machine = SendMachine(blob)
    context = machine.register(0x60024634)
    contexts = [list(struct.unpack('<6I', machine.uc.mem_read(context + 24 * s, 24)))
                for s in (0, 1)]
    assert contexts == [[1, 0x3000, 0x2000, 4, 0x60, 0x50],
                        [1, 0x3000, 0x3000, 0x27, 0x70, 0xa8]]
    # Real algorithm-2 DRAM-I/O metadata: relative entry offset 0x18.
    metadata = machine.register(0x600391f0)
    assert metadata == 0x6009ade8
    record = machine.register(metadata + 24)
    assert machine.uc.mem_read(record, 1) == b'\x01'
    assert machine.register(record + 12) == 0x18
    seeded = [(0x4016e038, (0x00568961, 0x001f0003)),
              (0x4016e150, (0x0070e761, 0x004f0003))]
    # Cross-check fixture words against both original algorithm-2 data blobs.
    for slot, (_, words) in enumerate(seeded):
        table = (0x600caafc, 0x600cab9c)[slot]
        descriptor = machine.register(table + 2 * 4)
        source = machine.register(descriptor + 8)
        assert bytes(machine.uc.mem_read(source + 0x18, 8)) == struct.pack('<II', *words)
    cases = []
    coefficient_cases = []
    address_cases = []
    for slot in (0, 1):
        obj = 0x20030000
        machine.checked(0x600238d4, obj, context + 24 * slot)
        for value in (0, 1, 0x45a9, 0xffff):
            for address, words in seeded:
                machine.uc.mem_write(address, struct.pack('<II', *words))
            machine.uc.reg_write(UC_ARM_REG_R2, metadata)
            machine.uc.reg_write(UC_ARM_REG_R3, value)
            machine.checked(0x60023b2e, obj, 1)
            address, words = seeded[slot]
            expected = (words[0], (words[1] & 0xffff0000) | value)
            assert machine.writes == [(address, 4, expected[0]), (address + 4, 4, expected[1])]
            other, other_words = seeded[1 - slot]
            assert bytes(machine.uc.mem_read(other, 8)) == struct.pack('<II', *other_words)
            cases.append({'slot': slot, 'value': value, 'writes': [
                {'runtime': hex(a), 'width': n, 'value': hex(v)} for a, n, v in machine.writes]})
        coefficient_metadata = machine.register(0x6003410c)
        assert machine.register(coefficient_metadata + 12) == 3
        for value in (0, 0x3f800000):
            machine.uc.mem_write(0x2003f000, bytes(8))  # Explicit smoothing arguments.
            machine.uc.reg_write(UC_ARM_REG_R2, coefficient_metadata)
            machine.uc.reg_write(UC_ARM_REG_R3, value)
            requests = machine.checked(0x60023a24, obj, 1)
            assert len(requests) == 1
            assert requests[0] == {'kind': 'coefficient', 'core': 1,
                                   'index': (0x63, 0x73)[slot], 'float_bits': value, 'smoothing': 0}
            assert machine.writes
            coefficient_cases.append({'slot': slot, 'requests': requests, 'writes': [
                {'runtime': hex(a), 'width': n, 'value': hex(v)} for a, n, v in machine.writes]})
    # Algorithm 19 has both base-address and relative read-address metadata.
    # Execute the original address arithmetic and direct window read/write too.
    address_metadata = machine.register(0x6003af00)
    assert address_metadata == 0x600a39dc
    address_fixtures = []
    for slot in (0, 1):
        descriptor = machine.register((0x600caafc, 0x600cab9c)[slot] + 19 * 4)
        offset, length, source = struct.unpack('<III', machine.uc.mem_read(descriptor, 12))
        data = bytes(machine.uc.mem_read(source, length))
        address_fixtures.append((0x4016e000 + offset, data))
    for slot in (0, 1):
        obj = 0x20030000
        machine.checked(0x600238d4, obj, context + 24 * slot)
        for delta in (0, 1, 123, 0x113a):
            for address, data in address_fixtures:
                machine.uc.mem_write(address, data)
            address, data = address_fixtures[slot]
            base_word = struct.unpack_from('<I', data)[0]
            before = struct.unpack_from('<II', data, 8)
            expected = ((before[0] & 0xff800000) | ((base_word & 0x7fffff) + delta), before[1])
            machine.uc.mem_write(0x2003f000, struct.pack('<I', delta))
            machine.uc.reg_write(UC_ARM_REG_R2, address_metadata)
            machine.uc.reg_write(UC_ARM_REG_R3, address_metadata - 24)
            machine.checked(0x6002397e, obj, 1)
            assert machine.writes == [(address + 8, 4, expected[0]), (address + 12, 4, expected[1])]
            other, other_data = address_fixtures[1 - slot]
            assert bytes(machine.uc.mem_read(other, len(other_data))) == other_data
            address_cases.append({'slot': slot, 'delta': delta, 'base_word': hex(base_word),
                                  'before': [hex(x) for x in before], 'writes': [
                {'runtime': hex(a), 'width': n, 'value': hex(v)} for a, n, v in machine.writes]})
    return {
        'constructor_runtime': '0x60024228', 'constructor_decoded_offset': '0x24228',
        'context_runtime': hex(context),
        'context_fields': ['core', 'source_program_halfword', 'destination_program_halfword',
                           'data_entry_base', 'coefficient_base', 'shared_port_base'],
        'slot_contexts': contexts,
        'metadata_runtime': hex(metadata), 'metadata_decoded_offset': hex(metadata - 0x60000000),
        'executed_runtime': ['0x600238d4', '0x60023b2e', '0x0100c7ca', '0x0100c206', '0x0100c0d0'],
        'executed_decoded_offsets': ['0x238d4', '0x23b2e', '0xdd056', '0xdca92', '0xdc95c'],
        'cases': cases, 'coefficient_cases': coefficient_cases, 'address_cases': address_cases,
        'address_metadata_runtime': hex(address_metadata),
        'address_wrapper_runtime': '0x6002397e', 'address_wrapper_decoded_offset': '0x2397e',
        'address_helper_runtime': '0x0100c5da', 'address_helper_decoded_offset': '0xdce66',
        'coefficient_metadata_runtime': hex(coefficient_metadata),
        'coefficient_wrapper_runtime': '0x60023a24', 'coefficient_wrapper_decoded_offset': '0x23a24',
        'coefficient_writer_runtime': '0x0100b5ea', 'coefficient_writer_decoded_offset': '0xdbe76',
        'stubs': [],
        'modeled': ['DSP data-memory window is ordinary read/write storage seeded with stock table entries',
                    'MMIO storage and readiness responses use the existing AuditMachine model'],
        'finding': 'Stock relative metadata resolves to distinct slot coefficients and data records; address updates use the selected slot base field.',
        'not_established': ['Full delay-buffer extents', 'Time units', 'DSP execution or MMIO timing'],
    }


def build_artifacts():
    from container_tool import COMPONENT_BY_NAME, component_unpacked
    from routing_hardware_audit import ORIGINAL_SHA256, MAIN_SHA256
    from routing_audio_extract import reconstruct

    stock = (ROOT / 'inputs/MX1_UPD.original.bin').read_bytes()
    assert sha(stock) == ORIGINAL_SHA256
    blob = component_unpacked(stock, COMPONENT_BY_NAME['app_main'])
    assert sha(blob) == MAIN_SHA256
    assert blob == (ROOT / 'analysis/container_app_main.bin').read_bytes()
    word = lambda address: struct.unpack_from('<I', blob, address - 0x60000000)[0]
    chunks = []
    artifacts = {}
    packets_by_name = {}
    controls, labels = audit_mixer_controls(blob)

    def add(name, chunk, image, *, trailer=False, **extra):
        start, length = chunk['program_offset'], chunk['length']
        data = logical_image(image)[start:start + length]
        packets = decode(data, start, gate=start == 0, trailer=trailer)
        packets_by_name[name] = packets
        source = chunk['source']
        info = {'name': name, 'core': chunk['core'], 'logical_start': start,
                'length_bytes': length, 'source_runtime': hex(source),
                'source_decoded_offset': hex(source - 0x60000000),
                'sha256': sha(data), 'packet_count': sum(p.kind == 'packet' for p in packets),
                'opaque_record_count': sum(p.kind != 'packet' for p in packets), **extra}
        chunks.append(info)
        # Source pointers refer to uploader input, not a naive linear byte map:
        # original boundary writes can consume a leading halfword specially.
        lines = [f'# {name}: DSP{chunk["core"]}; main source {source:#x}',
                 '# Logical byte offsets. Packet framing and bindings?/flow? are inferred.',
                 '# Raw words are authoritative; arithmetic/latency/width are not decoded.']
        lines.extend(listing_line(p, labels if chunk['core'] == 1 and name.startswith('dsp') else None)
                     for p in packets)
        artifacts[name + '.txt'] = '\n'.join(lines) + '\n'
        return info

    baseline, images = reconstruct()
    for chunk in baseline['chunks']:
        name = f'dsp{chunk["core"]}-{chunk["program_offset"]:04x}'
        add(name, chunk, images[chunk['core']], trailer=chunk['program_offset'] == 0x7ff2)
    factory, images = reconstruct(tables=(0x600cb780, 0x600bbed0), counts=(1, 0))
    add('factory-dsp0', factory['chunks'][0], images[0], trailer=True)
    for algorithm in range(20):
        for slot in (0, 1):
            descriptor = word((0x600caaac, 0x600cab4c)[slot] + algorithm * 4)
            report, images = reconstruct(tables=(0x600ba008, descriptor), counts=(0, 1))
            data_descriptor = word((0x600caafc, 0x600cab9c)[slot] + algorithm * 4)
            data_offset, data_length, data_source = struct.unpack_from('<III', blob, data_descriptor - 0x60000000)
            data_info = {'descriptor_runtime': hex(data_descriptor), 'offset_bytes': data_offset,
                         'length_bytes': data_length, 'source_runtime': hex(data_source)}
            if 0x60000000 <= data_source <= 0x60000000 + len(blob) - data_length:
                data = blob[data_source - 0x60000000:data_source - 0x60000000 + data_length]
                data_info['raw_entries_u32'] = [list(v) for v in struct.iter_unpack('<II', data)]
            else:
                data_info['unresolved'] = 'Source is runtime RAM; startup bytes are not assumed to be initialized effect data.'
            add(f'fx{algorithm:02d}-slot{slot}', report['chunks'][0], images[1],
                algorithm=algorithm, slot=slot, data=data_info)

    pairs = []
    for algorithm in range(20):
        left = packets_by_name[f'fx{algorithm:02d}-slot0']
        right = packets_by_name[f'fx{algorithm:02d}-slot1']
        assert len(left) == len(right)
        differences = []
        classes = Counter()
        lines = [f'# Algorithm {algorithm}: slot0 -> slot1 changed halfwords only.',
                 '# Labels describe observed encodings/deltas, not a complete memory ownership proof.']
        for p, q in zip(left, right):
            assert len(p.words) == len(q.words) and p.words[0] == q.words[0]
            for i, (x, y) in enumerate(zip(p.words, q.words)):
                if x == y:
                    continue
                kind = 'unclassified'
                if flow_target(p) is not None and i == 2 and y - x == 0x1000:
                    kind = 'flow_halfword_delta_1000'
                elif 0xc060 <= x <= 0xc06f and y - x == 0x10:
                    kind = 'coefficient_encoding_delta_10'
                elif x < 0x100 and y - x == 0x100:
                    kind = 'low_operand_delta_100'
                classes[kind] += 1
                differences.append({'slot0_offset': p.offset + i * 2, 'slot1_offset': q.offset + i * 2,
                                    'before': x, 'after': y, 'class': kind})
                lines.append(f'{p.offset+i*2:04x}/{q.offset+i*2:04x}: {x:04x} -> {y:04x} {kind}')
        artifacts[f'fx{algorithm:02d}-relocations.txt'] = '\n'.join(lines) + '\n'
        pairs.append({'algorithm': algorithm, 'same_packet_headers': True,
                      'changed_halfwords': len(differences), 'classes': dict(sorted(classes.items()))})

    # Independently bounded chunks supply the boundary set for candidate flow
    # targets. Preserve unresolved targets in the report instead of inventing a CFG.
    normal_starts = {core: {p.offset for name, ps in packets_by_name.items()
                           if name.startswith(f'dsp{core}-') for p in ps if p.kind == 'packet'}
                     for core in (0, 1)}
    flow = []
    for chunk in chunks:
        name = chunk['name']
        starts = {p.offset for p in packets_by_name[name] if p.kind == 'packet'}
        if name.startswith('dsp'):
            starts = normal_starts[chunk['core']]
        for packet in packets_by_name[name]:
            target = flow_target(packet)
            if target is not None:
                flow.append({'chunk': name, 'offset': packet.offset, 'mode': packet.words[1],
                             'target': target, 'target_is_packet_start': target in starts})
    counts = Counter(p.words[0] for ps in packets_by_name.values() for p in ps if p.kind == 'packet')
    mixer_bindings = {p.words[j] for name, ps in packets_by_name.items() if name.startswith('dsp1-')
                      for p in ps for _, j in binding_tail(p)}
    assert labels.keys() <= mixer_bindings, 'A callback coefficient has no matching mixer operand'
    report = {'scope': 'Partial stock ESC2 structural disassembly; no firmware modification',
              'original_update_sha256': ORIGINAL_SHA256, 'main_sha256': MAIN_SHA256,
              'chunks': chunks, 'packet_count': sum(counts.values()),
              'header_histogram': {f'{h:04x}': n for h, n in sorted(counts.items())},
              'slot_comparisons': pairs, 'candidate_flow_targets': flow,
              'mixer_control_anchors': controls,
              'contexts_and_data_updates': audit_contexts(blob),
              'limitations': ['Low-five-bit framing is corpus-supported inference, not a complete ISA definition.',
                              'Bindings and control flow are hypotheses; unknown operations remain raw.',
                              'Original ARM uploader runs; bulk DMA is modeled as copying and command writes as storage.',
                              'No DSP arithmetic, external delay RAM, cycle budget or physical audio is emulated.']}
    # Keep the review surface compact: one listing per core and effect pair.
    grouped = {f'dsp{core}.txt': '\n'.join(artifacts[c['name'] + '.txt'] for c in
               sorted(chunks, key=lambda c: c['logical_start']) if c['name'].startswith(f'dsp{core}-'))
               for core in (0, 1)}
    grouped['factory-dsp0.txt'] = artifacts['factory-dsp0.txt']
    for algorithm in range(20):
        grouped[f'fx{algorithm:02d}.txt'] = '\n'.join(artifacts[f'fx{algorithm:02d}-{suffix}.txt']
            for suffix in ('slot0', 'slot1', 'relocations'))
    grouped['report.json'] = json.dumps(report, indent=2) + '\n'
    return grouped, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare deterministic listings and report')
    args = parser.parse_args()
    artifacts, report = build_artifacts()
    if not args.check:
        OUT.mkdir(parents=True, exist_ok=True)
    for name, content in artifacts.items():
        path = OUT / name
        if args.check:
            assert path.read_text() == content, f'Disassembly evidence differs: {path}'
        else:
            path.write_text(content)
    print(json.dumps({'status': 'pass', 'chunks': len(report['chunks']),
                      'packets': report['packet_count'], 'effect_pairs': len(report['slot_comparisons']),
                      'original_data_update_cases': len(report['contexts_and_data_updates']['cases']),
                      'original_address_update_cases': len(report['contexts_and_data_updates']['address_cases']),
                      'original_coefficient_relocation_cases': len(report['contexts_and_data_updates']['coefficient_cases']),
                      'original_control_cases': sum(len(c['cases']) for c in report['mixer_control_anchors']),
                      'dsp_execution_tested': False}))


if __name__ == '__main__':
    main()
