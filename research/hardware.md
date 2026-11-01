# Roland MX-1 hardware investigation

Investigation date: 1 November 2026. Target: user-supplied `MX1_UPD.BIN`, SHA-256
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.

## What is established, and what is still a hypothesis

The interface roles, channel capacity and sample rates are documented by Roland.
The supplied firmware additionally exposes a distinct panel/sub-CPU image that
very strongly matches an **STM32F100 medium-density Cortex-M3**, with live GPIO
usage suggesting the **100-pin STM32F100V8 or STM32F100VB** variants. These are
firmware-derived identifications, not photographed chip markings.

The two larger application images identify the ESC2 software platform, according
to the main/container analysis. Related Roland service documents identify ESC2
as **MB8AA4181**, a custom mixed control/DSP component. That part number remains
**unconfirmed for this particular MX-1**. No trustworthy MX-1 internal-board
photograph, public service schematic, or BOM was located. The quantities of ESC2
packages, their external RAM/flash parts, and the wiring between them therefore
remain open. Two firmware images do not alone establish two physical chips.

## Documented external hardware

| Item | Established capability | Evidence |
|---|---|---|
| Computer connector | USB Type B, USB function/device role; audio and MIDI | Roland product specifications [R1] |
| Four AIRA connectors | USB Type A, host role; audio and MIDI | [R1], owner's manual [R2] |
| Bus power | Advertised for USB HOST 3 only | [R1], [R2] |
| Computer audio | 18 input and 18 output channels; 24-bit; 44.1/48/96 kHz | [R1] |
| USB speed | Hi-Speed USB | [R1] |
| Analog I/O conversion | 24-bit; 44.1/48/96 kHz | [R1] |
| S/PDIF | One coaxial connector, software-selectable input or output | [R1], [R2] |
| Rate conversion for AIRA inputs | MX-1 can convert fixed-96-kHz AIRA inputs to a 48/44.1-kHz system | Roland support [R3] |

“Only port 3 supplies bus power” is a documented product capability, not a
measurement that the other ports have no VBUS voltage at all. New bus-powered
devices should initially be tested on port 3 or with independently managed
power, after understanding the supported topology.

Roland's current specifications still name only the original four AIRA products.
The firmware release notes supersede that list: 1.03 added seven other Roland
models, 1.04 added JUNO-DS/XPS-30, and 1.05 added SYSTEM-8 [R4]. The broadening
already implemented by Roland is evidence that host compatibility is partly
software policy. It does not establish support for arbitrary USB Audio Class
devices.

## Implications for the two desired features

### A class-compliant interface for iOS

The existing **Type B computer port** already has the correct USB device role.
An iPhone/iPad acting as host can in principle occupy the role a Mac/PC currently
occupies. Physical host-role conversion of the Type A ports is unnecessary for
this path. The existing hardware's multichannel isochronous transfer capability
is useful evidence, but class compliance depends on descriptors, control
requests, sample-clock negotiation and stream behavior in the firmware.

Reversing the Type A ports' role cannot be assumed possible merely because USB
signals exist there. The controller capability, PHY wiring, VBUS power-switch
design and connector topology have not been verified. It is a much less
supported development direction than adapting the Type B function stack.

### Accepting class-compliant USB audio on AIRA ports

The four existing host ports already implement the essential host-side role
and transport audio from multiple attached instruments. Firmware work must
address descriptor parsing, interface/alternate-setting selection, supported
sample formats, endpoint scheduling and clock handling. Existing AIRA sample
rate conversion means a generic-input implementation may be able to reuse
conversion machinery rather than introducing it from scratch; this remains a
code-tracing question. MIDI tempo synchronization is separate from audio sample
clock synchronization.

The manufacturer signal-flow diagram shows one stereo audio path per host port
entering the USB channel processing [R5]. Expanding compatibility should first
target that existing stereo path. Supporting every channel of an arbitrary
multichannel interface would additionally require channel-selection policy and
possibly more transfer/buffering work; the front panel still supplies four
stereo USB strips.

## Panel/sub-CPU: reproducible direct evidence

### Extraction and verification

The embedded image is at original-file offset `0x40040`, length `0x4014` (16,404
bytes), loaded at `0x08000000`. Its SHA-256 is
`43812718e448b386ccfa0d578ff0700d27c2e9e734dbbb80c08af5b880d4a16d`.

Run from the packaged project root, with its requirements installed in the
local virtual environment:

```sh
.venv/bin/python sources/hardware/inspect_subcpu.py \
  inputs/MX1_UPD.original.bin sources/hardware --disassemble
```

The script requires the exact original firmware hash before using fixed offsets.
It extracts the sub-CPU image, checks the complete external-interrupt reserved
slot pattern against the STM32F100 low/medium-density layout, and emits
`subcpu_evidence.json` plus selected annotated assembly. It makes no device writes.

Ghidra independently imported this image as `ARM:LE:32:Cortex`, with its observed
RAM initialization mapped by `MX1SubcpuMap.java`. Automatic analysis/decompilation
exported **171 functions with zero reported decompiler failures**. This is useful
pseudocode, not recovered original C++ and not proof of correct types or function
boundaries throughout. The raw linear disassembly is supplementary only; literal
pools and tables can decode as plausible instructions.

### Why STM32F100 is a strong identification

The first two vector words are initial SP `0x200015b0` and Thumb reset vector
`0x08000315`. Peripheral literals and executed register accesses match STM32F1:

| Peripheral | Base address | Code evidence |
|---|---:|---|
| GPIOA | `0x40010800` | Initialization beginning `0x08000884` |
| GPIOB | `0x40010c00` | Same initialization function |
| GPIOC | `0x40011000` | Same initialization function |
| GPIOD | `0x40011400` | Same initialization function |
| GPIOE | `0x40011800` | Same initialization; live startup write at `0x0800295e` |
| ADC1 | `0x40012400` | Initialization at `0x08000638` |
| TIM1 | `0x40012c00` | Timer initialization and IRQ servicing |
| USART1 | `0x40013800` | Initialization at `0x08001354` |
| RCC | `0x40021000` | Clock initialization at `0x08000c64` |

The interrupt layout distinguishes the value line from a casual STM32F103 guess:
IRQs 19–22 and 43–53 are zero/reserved; IRQ54 and IRQ55 retain default handlers;
IRQ25 and IRQ37 have real handlers. These match ST's STM32F100xB startup template
and reference manual [S1, S2]. The runtime locations are:

| Interrupt | Vector address | Handler |
|---|---:|---:|
| TIM1 update/TIM16 | `0x080000a4` | `0x08000d35` (Thumb) |
| USART1 | `0x080000d4` | `0x08001135` (Thumb) |

The image's initialized RAM spans `0x20000000..0x2000009f`. Its observed startup
scatter table then clears `0x1510` bytes at `0x200000a0`, ending exactly at
`0x200015b0`. This exceeds a 4-KiB SRAM layout. Combined with the interrupt
template, it favors the medium-density 8-KiB SRAM STM32F100 parts.

### GPIO mapping recovered from executed initialization

`0x08002934` calls RCC setup, interrupt setup, GPIO initialization, ADC setup,
USART setup and timer setup. Thus these GPIO configurations are on the normal
startup path, rather than unused generic driver routines.

| Port | Analog inputs | Floating digital inputs | Push-pull outputs | Alternate function |
|---|---|---|---|---|
| A | 0–3 | 10 | 4–7 | 9: AF push-pull |
| B | — | 12–15 | 0, 1, 5–8 | — |
| C | — | 6–9 | 0–3, 10 | — |
| D | — | 0–5, 8, 9 | 6, 7, 10–15 | — |
| E | — | 7–10 | 4–6, 11–15 | — |

These masks come directly from the packed GPIO initialization structures in
`FUN_08000884`. Output speed is configured as 2 MHz, which is the GPIO edge-rate
setting, **not the CPU clock**. In particular, GPIOE pins are configured and used;
within the matching low/medium-density STM32F100 family, the relevant pins are
bonded in the LQFP100 variants [S3]. The best candidate is therefore
**STM32F100V8 or STM32F100VB**. The image cannot distinguish their 64/128-KiB flash
capacity or their temperature/speed suffix. Board photos or chip ID/flash-size
reads would settle this.

The four analog inputs and many digital scan pins are consistent with a panel
scanner driving multiplexers, LEDs and switch matrices. The exact connection
between those MCU pins and individual faders/knobs/buttons is not established by
this GPIO table alone. Do not label those physical panel nets without tracing
the scan tables and/or checking the board.

### Clock and serial link

The code's RCC clock-reporting routine contains an **HSE frequency constant of
24,000,000 Hz**, HSI 8,000,000 Hz and HSI/2 4,000,000 Hz. `SystemInit` enables HSE,
configures the PLL path, and switches the system clock to it. Together with the
STM32F100 maximum-frequency rating [S3], **24 MHz is the strong nominal sub-CPU
clock inference**. This is not a measurement of its oscillator.

USART1 initialization at `0x08001354` sets the baud parameter to `0xf424`, or
**62,500 baud**, with default 8-bit word length, one stop bit, no parity, no
hardware flow control and both TX/RX enabled. GPIO initialization sets PA9 to
alternate-function output and PA10 to floating input, consistent with unremapped
USART1. On the candidate LQFP100 package, ST lists PA9/PA10 as pins 68/69 [S3].
This is a useful starting point for a **passive logic-analyzer capture of the
panel communication**, once the actual chip and nets are identified.

The initializer resets AFIO and does not reassign PA13/PA14 in the observed GPIO
setup. Those pins are normally SWDIO/SWCLK on this family [S3]. Their physical
availability and debug access state on the MX-1 have not been verified. This
sub-CPU is a panel-control route; discovering its SWD access would not by itself
give access to the ESC2 audio/USB firmware.

## ESC2 family evidence from related Roland hardware

Roland's **FA-08 service notes** label its IC6 as `MB8AA4181 (ESC2)`, show separate
USB host (`UH`) and function (`UF`) signal pairs, external SPI boot flash,
SDRAM, and an unpopulated JTAG connection. They document configurable boot modes
including serial flash and internal-ROM boot, and ETM trace selection [E1].
These are leads for interpreting the MX-1 platform. They are not an MX-1 BOM or
a verified MX-1 recovery pinout.

An original TR-8 partial teardown identifies ESC2, multiple ISSI SDRAM devices and
an MX25L3206E 4-MiB SPI flash [E2]. Again, this verifies what existed in a related
AIRA generation, not what is soldered to this mixer.

An original BOSS GT-1 firmware investigation publishes the same `ESC91.000`
container marker and matching bootstrap layout, followed by `BSSESC2` identifiers
[E3]. It is useful as an independent family-format comparison. Its speculation
about the instruction set and generic electronic-component broker descriptions
are not reliable hardware identification and were not adopted here. The MX-1
binary's actual decoded instructions are stronger evidence.

No public datasheet for MB8AA4181 was located. In particular, do not replace an
unknown ESC2 core clock with the FA-08's printed peripheral/external clock values
or assign this part a guessed Cortex-M3 frequency from unrelated devices.

## Update, backup and recovery boundaries

Roland's documented update entry is **hold TAP while powering on**, connect the
computer port, copy the update into the exposed disk, eject and unplug, then
press TAP to begin programming. Completion is indicated by `Fin`. The release
page warns that interrupted programming may require servicing [R4].

This is evidence of an update mode, **not proof that an independent immutable
recovery loader survives arbitrary corrupted firmware**. Normal USB file-copy
updates should therefore be separated from any claim of recoverable experimental
flashing. The boot-image analysis elsewhere in this project should establish
which regions can be changed without touching the updater.

The supplementary manual documents a distinct backup/restore mode entered with
pad 1 held during power-on [R6]. That exports settings, not a complete flash
backup. Keep scene/combi backups separate from firmware and factory calibration
questions. The official page text writes `MX-1_UPD.BIN`, while the attachment is
named `MX1_UPD.BIN`; the actual validated updater filename should be taken from
the binary/update archive rather than silently renaming the user's file.

For hardware access, the highest-value missing evidence is a readable photograph
of each PCB side and its chip markings, followed by a topology check of the four
USB ports and identification of any programming headers. A USB descriptor dump
and captures of existing AIRA enumeration are useful without opening the unit.
Do not infer an exposed programming header's pin order from the FA-08 document.

## Search record and negative findings

Searches covered quoted MX-1/MX1 plus service notes, schematic, teardown,
motherboard, PCB, processor, DSP, ESC2, Fujitsu, repair, disassembly, Japanese
`分解`/`基板`/`内部`, and AIRA-related hardware discussions. Both search engines
were used. Searches did not yield an actual MX-1 service manual or clear internal
board images. Many apparent matches were Yamaha MX-1 amplifiers, Martin MX-1
lighting, Videonics MX-1 video mixers, or the much older Roland SH-2000's
internally named MX-1 circuit board; these were excluded. Generic repair service
pages had no usable internal hardware evidence. This is a record of what was
not found, not a claim such documentation does not exist.

## Source index

All URLs accessed 1 November 2026. Reference IDs are provided for the parent
investigation's citation tracking; primary sources should be opened by the final
reporting agent before citing them in chat.

| ID | Source and URL | Retrieval reference |
|---|---|---|
| R1 | Roland MX-1 specifications: https://www.roland.com/global/products/mx-1/ | `turn30search1`, `turn14view0` |
| R2 | Roland owner's manual: https://cdn.roland.com/assets/media/pdf/MX-1_e01_W.pdf | `turn11search8` |
| R3 | Roland, Changing the Sampling Rate: https://support.roland.com/hc/en-us/articles/205215985-MX-1-Changing-the-Sampling-Rate | `turn21search1` |
| R4 | Roland system program 1.05 and history: https://www.roland.com/global/support/by_product/mx-1/updates_drivers/82415302-0466-4c5c-be4e-138a8946d4a7/ | `turn7view1` |
| R5 | Roland signal-flow diagram: https://cdn.roland.com/assets/media/pdf/MX-1_Signalflow.pdf | `turn11search9`, `turn28search6` |
| R6 | Roland supplementary manual: https://cdn.roland.com/assets/media/pdf/MX-1_Supplementary_Manual_e01_W.pdf | `turn0search5` |
| S1 | STMicroelectronics STM32F100xB startup assembly: https://github.com/STMicroelectronics/cmsis-device-f1/blob/master/Source/Templates/gcc/startup_stm32f100xb.s | `turn33search1`, `turn34view0` |
| S2 | ST RM0041 reference manual: https://www.st.com/resource/en/reference_manual/cd00246267.pdf | `turn33search5` |
| S3 | ST STM32F100 low/medium-density datasheet: https://www.st.com/resource/en/datasheet/stm32f100c4.pdf | `turn34view1`, `turn39view0`, `turn39view1`, `turn39view2` |
| E1 | Roland FA-08 service notes, manufacturer document mirrored on ManualMachine: https://manualmachine.com/roland/fa08/9252142-service-notes/ | `turn14view2`, `turn17view1` |
| E2 | Original 2015 TR-8 partial teardown report: https://synth-diy.org/pipermail/synth-diy/2015-June/149151.html | `turn18search8` |
| E3 | Original BOSS GT-1 image investigation: https://webhamster.ru/mytetrashare/index/mtb0/17186974979qcubc1ew5 | `turn25search0` |

The DTM Station hands-on report at
https://www.dtmstation.com/archives/51954723.html (`turn14view1`) additionally
describes JD-Xi 44.1-kHz input converted within a 96-kHz MX-1 setup. The direct
Roland support statement [R3] was preferred for the core rate-conversion claim.
