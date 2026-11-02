"""Exact main-application guards for the internal-source panel hooks."""
import struct

from firmware_patch import exact_patch
from build_firmware import absolute_jump

UI_HOOKS = (
    (0x14692, '2de9f041844803f0defd', 'mx1_sources_ui_select_leds',
     'Stock SELECT LEDs plus blinking source-edit selection'),
    (0x10516, '114910b5083148806ff06300', 'mx1_sources_ui_press',
     'BD step press after original queue/held-key update'),
    (0x10538, '084910b514314880', 'mx1_sources_ui_release',
     'BD tap release or held-note edit completion'),
    (0x140C2, '2de9f04100221146e548', 'mx1_sources_ui_steps',
     'BD sixteen-step LED view; stock BFX/MFX views preserved'),
    (0x13740, '2de9fc4180460022', 'mx1_sources_ui_value',
     'Held BD note pitch overlay on three-character VALUE display'),
    (0x13356, 'feb50446c54804f07cff', 'mx1_sources_ui_tempo',
     'Held BD decay or SELECT source overlay on TEMPO display'),
)


def patch_ui(image: bytearray, symbols: dict, changes: list) -> None:
    exact_patch(image, 0xF5D8, struct.pack('<I', 0x60010B49),
                struct.pack('<I', symbols['mx1_sources_ui_event'] | 1), changes,
                'Panel event callback: source picker and held BD step encoders')
    for offset, old_hex, name, description in UI_HOOKS:
        old = bytes.fromhex(old_hex)
        replacement = absolute_jump(0x60000000 + offset, symbols[name])
        assert len(replacement) <= len(old) and (len(old) - len(replacement)) % 2 == 0
        replacement += bytes.fromhex('00bf') * ((len(old) - len(replacement)) // 2)
        exact_patch(image, offset, old, replacement, changes, description)
