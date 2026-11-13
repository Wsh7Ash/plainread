import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from plainread import (
    analyze,
    count_syllables,
    render_json,
    render_text,
    split_sentences,
    strip_markdown,
)
from plainread.cli import main

CLEAR = (
    "We ship on Monday. The team tests every build. "
    "Each release fixes one bug. You can read the notes."
)

DENSE = (
    "It was decided by the committee that, although the implementation of the "
    "aforementioned configuration mechanism was very arguably somewhat "
    "problematic in several important respects, a comprehensive reconsideration "
    "of the underlying assumptions should perhaps be undertaken by the relevant "
    "stakeholders prior to any further deployment activities being initiated."
)


def test_syllable_heuristic():
    assert count_syllables("table") == 2
    assert count_syllables("make") == 1
    assert count_syllables("readability") == 4
    assert count_syllables("cat") == 1
    assert count_syllables("!!!") == 0


def test_markdown_is_stripped():
    text = "# Title\n\nUse `pip install` and see [the docs](https://example.com).\n\n```\ncode block\n```\n"
    cleaned = strip_markdown(text)
    assert "code block" not in cleaned
    assert "pip install" not in cleaned
    assert "the docs" in cleaned
    assert "Title" in cleaned


def test_sentence_splitting():
    assert len(split_sentences("One. Two! Three?")) == 3
    assert split_sentences("No punctuation here") == ["No punctuation here"]


def test_clear_text_scores_well():
    report = analyze(CLEAR)
    assert report.words == 19
    assert report.sentences == 4
    assert report.avg_sentence_words == 4.8
    assert report.score >= 70
    assert report.band == "easy"
    assert report.passive_hits == 0


def test_dense_text_reports_issues():
    report = analyze(DENSE)
    assert report.long_sentences >= 1
    assert report.passive_hits >= 1
    assert report.score < 50
    assert report.band in {"dense", "hard"}
    assert any("passive" in s.lower() for s in report.suggestions)
    assert report.hedges.get("very") == 1


def test_rendering_and_json():
    report = analyze(DENSE)
    text = render_text(report, "dense.txt")
    assert "plainread report - dense.txt" in text
    assert "Score:" in text
    payload = json.loads(render_json(report, "dense.txt"))
    assert payload["target"] == "dense.txt"
    assert payload["score"] == report.score
    assert payload["band"] == report.band


def test_cli_gate_and_stdin(tmp_path, monkeypatch):
    path = tmp_path / "clear.md"
    path.write_text(CLEAR, encoding="utf-8")
    assert main([str(path)]) == 0
    assert main([str(path), "--fail-under", "60"]) == 0
    assert main([str(path), "--json"]) == 0

    dense = tmp_path / "dense.md"
    dense.write_text(DENSE, encoding="utf-8")
    assert main([str(dense), "--fail-under", "50"]) == 1

    assert main([str(tmp_path / "missing.md")]) == 2

    import io

    monkeypatch.setattr(sys, "stdin", io.StringIO(CLEAR))
    assert main(["-"]) == 0
