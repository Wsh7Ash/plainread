# PROJECT_SPEC — plainread

- **Name:** plainread
- **Category:** content-tool
- **Target user:** technical writers, documentation maintainers, non-developers
  who publish guides
- **Problem:** style advice is abstract; authors cannot see which sentences,
  constructions and words drag a document down.
- **Solution:** a local CLI that scores readability and lists concrete fixes.
- **Core workflow:** `plainread <file>` → score, metrics, specific suggestions.
- **Must-have features:** Markdown stripping, Flesch metrics, long-sentence,
  passive and hedge detection, repeated openers, overused words, JSON output,
  CI gate, stdin support.
- **Nice-to-have features:** per-section breakdown, glossary consistency.
- **Stack:** Python 3.10+, standard library only.
- **Test strategy:** pinned syllable counts, Markdown stripping, clear vs dense
  documents, JSON/text rendering, CLI gate and error codes.
- **Demo/result strategy:** analyse `examples/dense.md` and `examples/clear.md`,
  store reports in `results/`.
- **Safety considerations:** local files only, no network, no code execution.
- **Definition of done:** tests pass, install works, demo output recorded,
  score documented, no secrets.
