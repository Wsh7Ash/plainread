# Usage

## Everyday editing

```shell
plainread draft.md
```

Read the suggestions list first — it names the exact problem (how many sentences
to split, which opener repeats), which is more actionable than the score alone.

## Checking a documentation set in CI

```shell
for file in docs/*.md README.md; do
  plainread "$file" --fail-under 50 --json --out "results/$(basename "$file").json" || exit 1
done
```

Start with a gate near your current average, then raise it as pages improve.

## Standard input

```shell
pbpaste | plainread -            # macOS
Get-Clipboard | plainread -      # PowerShell
```

## Tuning the long-sentence limit

Technical text often needs longer sentences than marketing copy. Use
`--max-sentence 30` for reference pages and `--max-sentence 18` for onboarding
guides.

## Library use

```python
from plainread import analyze, render_text

report = analyze(open("guide.md", encoding="utf-8").read())
print(report.score, report.band)
print(render_text(report, "guide.md"))
```

## What the numbers mean

- **Flesch Reading Ease**: higher is easier. 60–70 corresponds to plain English.
- **Flesch-Kincaid grade**: US school grade needed to read the text.
- **Score**: the Flesch value after penalties for long sentences, passive voice
  and hedges. Use it for trends, not as an absolute grade.
