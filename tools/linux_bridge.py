#!/usr/bin/env python3
"""Plan/configure a Linux USB UAC2 bridge for the MX-1.

Default and every command without --apply are read-only. This is an untested
hardware prototype, not MX-1 firmware. See research/linux-bridge.md.
Requires Python 3.9+, Linux configfs/USB UDC, snd-usb-audio, and alsaloop built
with libsamplerate. No dependencies are installed and no boot files are edited.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time

CONFIG_ROOT = Path("/sys/kernel/config/usb_gadget")
UDC_ROOT = Path("/sys/class/udc")
ASOUND_ROOT = Path("/proc/asound")
GADGET_NAME = "mx1_ios_bridge"
MANUFACTURER = "MX1 research"
PRODUCT = "MX1 Linux UAC2 Bridge"
GADGET = CONFIG_ROOT / GADGET_NAME
ID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
UDC_RE = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")


def read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except (OSError, UnicodeError):
        return None


def integer(text: str) -> int:
    return int(text, 0)


def card_id(text: str) -> str:
    if not ID_RE.fullmatch(text):
        raise argparse.ArgumentTypeError("Use an ALSA card ID or numeric index, not a PCM expression")
    return text


def inspect() -> dict:
    """Read only sysfs/procfs plus executable presence; never open audio devices."""
    cards = []
    for path in sorted(ASOUND_ROOT.glob("card[0-9]*")):
        if not re.fullmatch(r"card\d+", path.name):
            continue
        cards.append({"index": int(path.name[4:]), "id": read_text(path / "id"),
                      "usb_id": read_text(path / "usbid"),
                      "usb_streams": {p.name: read_text(p) for p in path.glob("stream[0-9]*")}})
    udcs = [{"name": p.name, "state": read_text(p / "state"),
             "maximum_speed": read_text(p / "maximum_speed"),
             "current_speed": read_text(p / "current_speed"),
             "function": read_text(p / "function")}
            for p in sorted(UDC_ROOT.glob("*"))]
    gadgets = [{"name": p.name, "udc": read_text(p / "UDC"),
                "product": read_text(p / "strings/0x409/product")}
               for p in sorted(CONFIG_ROOT.glob("*")) if p.is_dir()]
    return {"mode": "read-only inventory", "kernel": os.uname().release,
            "configfs_gadget_directory_present": CONFIG_ROOT.is_dir(),
            "udcs": udcs, "sound_cards": cards, "existing_gadgets": gadgets,
            "programs": {name: shutil.which(name) for name in ("alsaloop", "aplay", "arecord", "lsusb")}}


def validate(args) -> None:
    if not 1 <= args.vid <= 0xFFFF or not 1 <= args.pid <= 0xFFFF:
        raise ValueError("VID and PID must each be in 1..65535")
    if args.udc and not UDC_RE.fullmatch(args.udc):
        raise ValueError("Invalid UDC name")
    if args.latency_us is not None and not 1000 <= args.latency_us <= 500000:
        raise ValueError("Initial target latency must be 1000..500000 microseconds")
    if not 0 <= args.seconds <= 100000:
        raise ValueError("Duration must be 0 (until interrupted) or 1..100000 seconds")
    if not 0 <= args.max_power_ma <= 500:
        raise ValueError("USB 2 MaxPower must be 0..500 mA")


def configuration(args) -> dict:
    """Return exact requested configfs fields, all relative to our gadget."""
    mask = hex((1 << args.channels) - 1)
    fields = {
        "idVendor": hex(args.vid), "idProduct": hex(args.pid),
        "bcdUSB": "0x0200", "bcdDevice": "0x0100",
        "bDeviceClass": "0xef", "bDeviceSubClass": "0x02", "bDeviceProtocol": "0x01",
        "strings/0x409/manufacturer": MANUFACTURER,
        "strings/0x409/product": PRODUCT,
        "strings/0x409/serialnumber": "mx1-bridge-prototype-001",
        "configs/c.1/strings/0x409/configuration": "UAC2 audio bridge",
        "configs/c.1/bmAttributes": "0xc0" if args.power_mode != "bus" else "0x80",
        "configs/c.1/MaxPower": "0" if args.power_mode != "bus" else str(args.max_power_ma),
    }
    function = {"c_chmask": mask, "p_chmask": mask,
                "c_srate": str(args.rate), "p_srate": str(args.rate),
                "c_ssize": "4", "p_ssize": "4", "c_sync": "async",
                "c_hs_bint": "1", "p_hs_bint": "1", "req_number": "8",
                "c_mute_present": "0", "p_mute_present": "0",
                "c_volume_present": "0", "p_volume_present": "0"}
    fields.update({f"functions/uac2.bridge/{key}": value for key, value in function.items()})
    return fields


def requested_latency(args) -> int:
    # u_audio commonly limits a hardware buffer to PAGE_SIZE*16 bytes. A 50 ms
    # 18-channel S32 buffer would already exceed 64 KiB at 48 kHz. Keep the
    # multichannel starting target at 240 frames; negotiation is still required.
    if args.latency_us is not None:
        return args.latency_us
    return 50000 if args.channels == 2 else round(240 * 1000000 / args.rate)


def route_commands(args) -> list[tuple[str, list[str]]]:
    mx1 = f"hw:CARD={args.mx1_card},DEV=0"
    gadget = f"hw:CARD={args.gadget_card},DEV=0"
    common = ["-f", "S32_LE", "-r", str(args.rate), "-c", str(args.channels),
              "-t", str(requested_latency(args)), "-S", "samplerate", "-A", "1", "-v"]
    if args.seconds:
        common += ["-s", str(args.seconds)]
    # Direction names refer to the external iOS host, not ALSA gadget naming.
    return [("iOS playback -> gadget capture -> MX-1 playback",
             ["alsaloop", "-C", gadget, "-P", mx1] + common),
            ("MX-1 capture -> gadget playback -> iOS recording",
             ["alsaloop", "-C", mx1, "-P", gadget] + common)]


def plan(args) -> dict:
    return {
        "status": "UNTESTED HARDWARE PROTOTYPE; this plan does not modify the system",
        "topology": ["MX-1 USB-B -> Linux independent USB host port",
                     "Linux UDC port -> iOS USB host port/host adapter"],
        "gadget_path": str(GADGET),
        "selected_udc": args.udc or "choose the single free physical UDC at apply time",
        "channels_each_direction": args.channels, "sample_rate": args.rate,
        "requested_route_latency_us": requested_latency(args),
        "format": "S32_LE, four bytes per sample; MX-1 source precision remains 24 bits",
        "minimum_audio_payload_bytes_per_125us_per_direction": args.channels * 4 * args.rate / 8000,
        "power_mode": args.power_mode or "self, pending explicit --power-mode self before apply",
        "create_directories": ["strings/0x409", "configs/c.1/strings/0x409", "functions/uac2.bridge"],
        "write_fields": configuration(args),
        "create_symlink": {"configs/c.1/uac2.bridge": "../../functions/uac2.bridge"},
        "last_setup_write": "selected UDC name -> UDC",
        "routes": [{"direction": label, "argv": argv, "shell_display": shlex.join(argv)}
                   for label, argv in route_commands(args)],
        "constraints": ["Independent physical USB host and UDC controllers are required",
                        "Use one advertised nominal rate matching the MX-1 front-panel setting",
                        "An 18-channel profile requires a high-speed gadget link",
                        "The 18-bit channel mask assigns USB spatial labels; verify app channel ordering",
                        "No MIDI is configured; no MX-1 USB-A behavior is changed",
                        "Route latency is an initial buffering target, not a measured latency",
                        "alsaloop must be compiled with libsamplerate; hardware validation is pending"],
    }


def choose_udc(args) -> str:
    names = [p.name for p in UDC_ROOT.iterdir()] if UDC_ROOT.is_dir() else []
    if args.udc:
        if args.udc not in names:
            raise RuntimeError(f"UDC {args.udc!r} is not present; run inspect")
        selected = args.udc
    elif len(names) == 1:
        selected = names[0]
    else:
        raise RuntimeError("Specify --udc using inspect; exactly one UDC could not be selected")
    for entry in CONFIG_ROOT.glob("*/UDC"):
        if read_text(entry) == selected:
            raise RuntimeError(f"UDC already bound by {entry.parent}; no existing gadget will be changed")
    function = read_text(UDC_ROOT / selected / "function")
    if function:
        raise RuntimeError(f"UDC reports an existing function: {function!r}")
    speed = read_text(UDC_ROOT / selected / "maximum_speed")
    if speed in {"low-speed", "full-speed"}:
        raise RuntimeError(f"This prototype requires a high-speed UDC, found {speed}")
    return selected


def write_attr(relative: str, value: str) -> None:
    path = GADGET / relative
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Required configfs attribute missing: {path}; use a kernel providing this UAC2 ABI")
    path.write_text(value + "\n")


def setup(args) -> None:
    if os.geteuid() != 0:
        raise RuntimeError("setup --apply needs root to configure configfs")
    if not args.power_mode:
        raise RuntimeError("Specify --power-mode self or bus to match the actual board power arrangement")
    if args.power_mode == "bus" and args.max_power_ma == 0:
        raise RuntimeError("Bus-powered mode requires a truthful nonzero --max-power-ma")
    if not CONFIG_ROOT.is_dir():
        raise RuntimeError("configfs USB gadget root is absent. Load libcomposite and mount configfs first; see report")
    if GADGET.exists():
        raise RuntimeError(f"{GADGET} already exists; inspect it, then use this tool's teardown if it is ours")
    udc = choose_udc(args)
    created: list[Path] = []
    try:
        GADGET.mkdir()
        created.append(GADGET)
        for relative in ("strings/0x409", "configs/c.1", "configs/c.1/strings/0x409", "functions/uac2.bridge"):
            path = GADGET / relative
            path.mkdir()
            created.append(path)
        for relative, value in configuration(args).items():
            write_attr(relative, value)
        link = GADGET / "configs/c.1/uac2.bridge"
        link.symlink_to("../../functions/uac2.bridge")
        created.append(link)
        # Binding is the only point at which the external iOS host sees a device.
        write_attr("UDC", udc)
        print(f"Bound {GADGET_NAME} to {udc}. Connect iOS, then inspect card IDs and start routes separately.")
    except Exception:
        try:
            if (GADGET / "UDC").exists():
                (GADGET / "UDC").write_text("\n")
            for path in reversed(created):
                if path.is_symlink():
                    path.unlink()
                else:
                    path.rmdir()
        except OSError as cleanup_error:
            print(f"Partial gadget remains at {GADGET}: {cleanup_error}", file=sys.stderr)
        raise


def is_ours() -> bool:
    return (read_text(GADGET / "strings/0x409/manufacturer") == MANUFACTURER
            and read_text(GADGET / "strings/0x409/product") == PRODUCT
            and (GADGET / "functions/uac2.bridge").is_dir())


def teardown() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("teardown --apply needs root")
    if not is_ours():
        raise RuntimeError("Gadget ownership markers do not match; refusing to remove it")
    link = GADGET / "configs/c.1/uac2.bridge"
    if not link.is_symlink() or link.resolve() != (GADGET / "functions/uac2.bridge").resolve():
        raise RuntimeError("Gadget function link differs from this tool's configuration")
    write_attr("UDC", "")
    link.unlink()
    for relative in ("functions/uac2.bridge", "configs/c.1/strings/0x409", "configs/c.1", "strings/0x409"):
        (GADGET / relative).rmdir()
    GADGET.rmdir()
    print("Removed this bridge gadget. Loaded kernel modules and configfs mount remain available.")


def resolve_card(identifier: str) -> Path:
    for path in ASOUND_ROOT.glob("card[0-9]*"):
        if path.name == f"card{identifier}" or read_text(path / "id") == identifier:
            return path
    raise RuntimeError(f"ALSA card {identifier!r} was not found; run inspect and use the reported ID")


def route(args) -> int:
    if not shutil.which("alsaloop"):
        raise RuntimeError("alsaloop is missing; install/build alsa-utils with libsamplerate support")
    mx1 = resolve_card(args.mx1_card)
    gadget = resolve_card(args.gadget_card)
    if mx1 == gadget:
        raise RuntimeError("MX-1 and gadget card IDs refer to the same card")
    if read_text(mx1 / "usbid") != "0582:01a3":
        raise RuntimeError("The selected MX-1 card does not report USB ID 0582:01a3")
    if not is_ours():
        raise RuntimeError("Create this tool's UAC2 gadget first")
    for relative, expected in configuration(args).items():
        if relative.startswith("functions/"):
            actual = read_text(GADGET / relative)
            # Numeric configfs fields may be read back as decimal or hex.
            try:
                matches = int(actual or "", 0) == int(expected, 0)
            except ValueError:
                matches = actual == expected
            if not matches:
                raise RuntimeError(f"Gadget setting {relative} is {actual!r}, expected {expected!r}; match setup arguments")
    udc = read_text(GADGET / "UDC")
    if not udc:
        raise RuntimeError("Gadget is not bound to a UDC")
    current_speed = read_text(UDC_ROOT / udc / "current_speed")
    if args.channels == 18 and current_speed not in {"high-speed", "super-speed", "super-speed-plus"}:
        raise RuntimeError(f"18 channels require an active high-speed-or-faster gadget link, found {current_speed!r}")
    if read_text(UDC_ROOT / udc / "state") != "configured":
        raise RuntimeError("USB host has not configured the gadget; connect/unlock iOS and select its audio interface")
    # No shell; a card name cannot inject commands or arbitrary ALSA definitions.
    processes: list[subprocess.Popen] = []
    try:
        for label, argv in route_commands(args):
            print(label + ": " + shlex.join(argv), flush=True)
            processes.append(subprocess.Popen(argv))
        while True:
            statuses = [p.poll() for p in processes]
            if any(status is not None for status in statuses):
                if args.seconds and all(status == 0 for status in statuses):
                    return 0
                # A timed route may finish fractionally before its partner.
                if args.seconds and all(status in (0, None) for status in statuses):
                    for process in processes:
                        process.wait(timeout=5)
                    return 0 if all(p.returncode == 0 for p in processes) else 1
                print("A route exited; stopping the paired route. Check ALSA format, clock and xrun messages.", file=sys.stderr)
                return 1
            time.sleep(0.25)
    except KeyboardInterrupt:
        return 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=("inspect", "plan", "setup", "route", "teardown"), nargs="?", default="inspect")
    p.add_argument("--apply", action="store_true", help="perform setup, route, or teardown; otherwise read-only")
    p.add_argument("--channels", type=int, choices=(2, 18), default=2)
    p.add_argument("--rate", type=int, choices=(44100, 48000, 96000), default=48000)
    p.add_argument("--mx1-card", type=card_id, default="MX1", help="replace with the ID from inspect")
    p.add_argument("--gadget-card", type=card_id, default="UAC2Gadget", help="replace with the ID from inspect")
    p.add_argument("--udc", help="exact controller name from /sys/class/udc")
    p.add_argument("--power-mode", choices=("self", "bus"), help="required for setup --apply; match actual hardware power")
    p.add_argument("--max-power-ma", type=int, default=100, help="actual requested VBUS current, for bus-powered mode")
    p.add_argument("--vid", type=integer, default=0x1d6b, help="prototype Linux gadget VID; not a Roland identity")
    p.add_argument("--pid", type=integer, default=0x0104, help="prototype Linux composite gadget PID")
    p.add_argument("--latency-us", type=int, help="default: stereo 50000 us; 18 channels 240 sample frames")
    p.add_argument("--seconds", type=int, default=0, help="routing duration; 0 runs until Ctrl-C")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        validate(args)
        if args.command == "inspect":
            print(json.dumps(inspect(), indent=2))
        elif args.command == "plan" or not args.apply:
            output = plan(args)
            output["requested_action"] = args.command
            if args.command == "teardown":
                output = {"mode": "read-only teardown plan", "gadget_path": str(GADGET),
                          "actions": ["verify ownership", "unbind UDC", "remove only this gadget's known objects"]}
            print(json.dumps(output, indent=2))
        elif args.command == "setup":
            setup(args)
        elif args.command == "route":
            return route(args)
        elif args.command == "teardown":
            teardown()
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"Bridge stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
