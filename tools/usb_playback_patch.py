"""Frozen main-app playback overwrite contract; original bytes remain guarded."""
from firmware_patch import exact_patch
from container_tool import FormatError, sha256

ORIGINAL = bytes.fromhex(
    "3878b04c002548b1d4f86c01000705d5d4f8d800c0f30a00f8603d70dff8a892"
    "dff8b082a949d9f80400a94edff8a4a24ff0004208f10808022805d04b460128"
    "07d0032867d00be0d4f86c01000714d406e0d4f86c01000702d5b86801280cd0"
    "d4f86c01000777d5b868012802d00120c9f804000120387097e0d4f87c019346"
    "c0f3034002284ff000001bd00b46d4f8f411009159451bd146f820301ee01028"
    "01d011280ed1d4f8f42100925a4502d146f8201008e0caf80020d8f8002046f8"
    "202001e046f82050401c1228e7db08e0caf80010d8f8001046f82010401c1228"
    "d5dbf8684838f860f868902803d00220c9f804005fe078490020d4f8f42141f8"
    "2020401c2428f8db3d70c9f800100321c9f804104fe0d4f87c01c0f303400228"
    "4ff000000ad093468946196804c9009219605a4521d146f8209024e096468b46"
    "d14603e0102808d0112806d046f82050401c1228f6db19e022e0196804c90092"
    "1960724502d146f820b0f1e7c9f80020d8f8001046f82010eae7caf80020d8f8"
    "001046f82010401c1228cedb52481a68903082420fd301203870022058600ae0"
    "c9f804503d704ff0000c002046f82050401c1228fadb"
)

def patch_playback(image, replacement, changes):
    if len(replacement) != len(ORIGINAL) or len(ORIGINAL) != 438:
        raise FormatError("USB playback replacement exceeds original instruction window")
    exact_patch(image, 0xda0ec, ORIGINAL, replacement, changes,
                "USB playback: frame-sized packet accounting and alternate-aware buffered tails")
    changes[-1]["runtime_address"] = 0x01009860
    return {
        "component": "app_main", "decoded_offset": 0xda0ec,
        "runtime_address": 0x01009860, "end_exclusive": 0x01009a16,
        "length": 438, "original_sha256": sha256(ORIGINAL),
        "replacement_sha256": sha256(replacement),
        "capture_continuation": 0x01009a16,
        "alternate_state": {"address": 0x010173f2, "size": 1,
                            "reservation_growth": 0, "initialization": "Existing BSS clear"},
        "abi": "Original callback frame and phase prefix retained; no calls/extra stack; r12=1 preserved; original capture and epilogue retained",
        "buffer": {"start": 0x20000a10, "end_exclusive": 0x20000aa0,
                   "frame_bytes": [8, 72], "tail_frames": [1, 2]},
    }
