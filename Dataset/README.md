# AIS3 Bench27 structured dataset

This directory contains only original agent transcripts, official/reference writeups, and their structured JSON extractions.

## Layout

```text
Dataset/
  README.md
  INDEX.md
  PROMPT.md
  writeups/<task>/
    reference.md
    agent/<solver>.md
  json/<task>/
    reference.json
    agent/<solver>/run-XX.json
```

There are 27 challenge folders, 942 valid agent-run JSON files, and 27 reference JSON files. Three source runs marked as harness or generation errors were intentionally not converted.

The `C`, `R`, and `D` prefixes mean Contaminated, Recent, and Deep. Frontier-generated reference material is not included. The `opus-4.8` files under `agent` are genuine agent solve transcripts and remain part of the dataset.

See `INDEX.md` for task-level solve counts and `PROMPT.md` for the exact extraction rules.
