# plainread

**A readability score and concrete plain-language fixes for any Markdown or
text file — built for people who write documentation, not code.**

## Why

Style guides say "write plainly" but never tell you which sentence is the
problem. `plainread` reads a file, strips Markdown syntax, and returns a 0–100
score plus the specific culprits: overlong sentences, passive constructions,
hedge words, repeated sentence openers and overused terms. It adds no
dependencies and makes no network calls, so drafts stay local.

## Features

- Flesch Reading Ease and Flesch-Kincaid grade with a syllable heuristic tuned
  for ordinary English prose
- Long-sentence detection with a configurable word limit
- Passive-voice and hedge-word detection with counts
- Repeated sentence openers and overused content words
- 0–100 score with four bands: easy, plain, dense, hard
- Text or JSON output, optional CI gate with `--fail-under`
- Reads a file or standard input (`-`)

## Example output

Output for `examples/dense.md` (reproduced in `RESULTS.md`):

```text
plainread report - examples/dense.md
==================================================
Score: 0/100 (hard)
Words: 108   Sentences: 3   Paragraphs: 2
Average sentence: 36.0 words
Flesch Reading Ease: 3.4   Flesch-Kincaid grade: 21.7
Long sentences: 2
Passive constructions: 9
Hedges: arguably x1, perhaps x1, somewhat x1, very x2

Suggestions:
  - Split 2 sentence(s) longer than 25 words.
  - Rewrite 9 passive construction(s) in active voice.
  - Remove or replace 5 filler/hedge word(s).
```

## Architecture

```text
src/plainread/__init__.py   text cleaning, metrics, scoring, renderers
src/plainread/cli.py        file/stdin handling and exit codes
tests/test_plainread.py     metric and CLI coverage
```

`strip_markdown` removes fences, inline code, links and emphasis before
analysis so code samples never distort the score. `analyze` computes counts in
one pass and returns a `Report` dataclass used by both renderers.

## Requirements

- Python 3.10+ (standard library only)
- pytest for tests

## Installation

```shell
git clone https://github.com/Wsh7Ash/plainread.git
cd plainread
python -m pip install -e .
```

## Quick start

```shell
plainread README.md
cat draft.txt | plainread -
```

## Usage

```shell
# Machine-readable report
plainread docs/guide.md --json --out results/guide.json

# Fail CI when a document drops below 55
plainread docs/guide.md --fail-under 55

# Report sentences longer than 20 words instead of 25
plainread docs/guide.md --max-sentence 20
```

Exit codes: `0` ok, `1` score below `--fail-under`, `2` unreadable/empty input.

## Configuration

Flags only: `--max-sentence`, `--fail-under`, `--json`, `--out`.

## Testing

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Project structure

```text
plainread/
├─ src/plainread/       analyser + CLI
├─ tests/               pytest suite
├─ examples/            sample documents
├─ docs/                architecture, usage, spec
├─ results/             generated reports
└─ .github/workflows/   CI
```

## Limitations

- Flesch formulas are calibrated for English prose; scores for other languages
  or highly technical text are indicative only.
- The syllable counter is heuristic and miscounts some loanwords and acronyms.
- Passive-voice detection is regex based; it catches common `be + participle`
  forms but not every construction.
- Markdown is stripped, not parsed, so unusual syntax may leak into word counts.

## Roadmap

- Optional per-heading breakdown
- Terminology consistency check against a glossary file
- HTML report output

## Security notes

The tool reads local files only, performs no network access and executes no
content from the analysed document.

## License

MIT — see `LICENSE`.
