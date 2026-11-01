## Problem

What behavior or evidence needs to change, and why?

## Change

Describe the resulting behavior and the parts of the firmware/tooling affected.

## Verification

Record the commands and results. The standard offline checks are:

```sh
python tools/reproduce.py
python tools/check_reproduction.py --check-committed
```

If candidate bytes change intentionally, include the rebuilt candidates and
matching evidence in the commit, and explain the changed hashes. Distinguish
offline checks from any physical hardware measurements.

## Remaining limitations

Identify relevant untested behavior or follow-up evidence needed.
