# Internal sources — retired

NSE/BD generators, their pad editor and the blinking SELECT mode are removed
from the maintained firmware. Their sample renderer caused a reproducible
selection freeze; bypassing it stopped that freeze. The precise cause remains
unresolved, and generator audio was never validated.

See [the generator/DSP handoff](GENERATOR_RESEARCH.md) for exact image identities,
observations, memory findings, original addresses, source-history pointers and
requirements for any future experiment. The [import provenance](../evidence/internal-sources-import-20261102/README.md)
remains preserved. Current controls are in [CHANNEL_ROUTING.md](CHANNEL_ROUTING.md).
