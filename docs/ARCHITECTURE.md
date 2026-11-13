# Architecture

## Pipeline

```text
raw file text
   │
   ▼ strip_markdown()      remove fences, inline code, links, HTML, emphasis
cleaned prose
   │
   ├─► split_sentences() ─► sentence lengths, openers
   ├─► words_of() ────────► word/syllable counts, overuse
   └─► regexes ───────────► passive hits, hedges
   │
   ▼
Report (dataclass)
   │
   ├─► render_text()
   └─► render_json()
```

## Scoring

```text
flesch = 206.835 − 1.015 × (words / sentences) − 84.6 × (syllables / words)
grade  =   0.39 × (words / sentences) + 11.8 × (syllables / words) − 15.59
score  = clamp(flesch − 10×long_share − min(15, 1.5×passive) − min(10, hedges), 0, 100)
```

Bands: `easy ≥ 70`, `plain ≥ 50`, `dense ≥ 30`, otherwise `hard`. The score is a
summary of the Flesch result after style penalties, not a separate standard.

## Decisions

**Strip before counting.** Code samples and URLs inflate syllable counts, so
Markdown constructs are removed before any metric is computed.

**Heuristic syllables.** English syllable counting is inherently approximate;
`count_syllables` counts vowel groups, subtracts a final silent `e`, and adds
one for consonant + `le`. Tests pin the intended behaviour of known words.

**Dataclass output.** All metrics live in `Report`, so text and JSON rendering
share one source of truth and library users avoid parsing strings.

## Error handling

Empty input is rejected by the CLI with exit code 2. The analyser itself never
divides by zero: sentence and word counts fall back to 1.

## Thresholds

`--max-sentence` affects both the long-sentence count and the penalty through
`long_sentence_share`. `--fail-under` compares the final clamped score.
