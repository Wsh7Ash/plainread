# Contributing

## Setup

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Changing the scoring

The Flesch formulas are fixed standard formulas; do not adjust their constants.
Style penalties (`long_share`, passive, hedges) live in `analyze()` and must be
documented in `docs/ARCHITECTURE.md` when changed.

## Adding a check

1. Compute the metric in `analyze()`.
2. Add it to `Report` and both renderers.
3. Add one positive and one negative test.
4. Explain the user-facing wording in the README.

## Style

- Standard library only.
- Keep the analyser free of file I/O; the CLI owns reading and writing.
