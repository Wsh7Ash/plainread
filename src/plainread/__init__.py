"""plainread - a plain-language report for people who write, not code.

The analyser strips Markdown noise, counts words and sentences, estimates
syllables, and reports Flesch Reading Ease, Flesch-Kincaid grade plus concrete
style issues: long sentences, passive constructions, hedges, repeated sentence
openers and overused words.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Iterable

HEDGES = (
    "very", "really", "quite", "just", "actually", "basically", "somewhat",
    "perhaps", "maybe", "arguably", "fairly", "rather", "possibly", "simply",
)

STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "have", "will",
    "your", "their", "there", "they", "them", "then", "than", "into", "about",
    "when", "what", "which", "while", "were", "been", "being", "also", "would",
    "could", "should", "more", "most", "much", "some", "such", "only", "other",
    "these", "those", "each", "because", "after", "before", "over", "under",
    "between", "through", "where", "here", "does", "did", "can", "may",
}

_PASSIVE = re.compile(
    r"\b(?:am|is|are|was|were|be|been|being)\s+"
    r"(?:\w+(?:ed|en)|shown|made|done|given|taken|known|seen|held|built)\b",
    re.IGNORECASE,
)


@dataclass
class Report:
    words: int
    sentences: int
    paragraphs: int
    syllables: int
    avg_sentence_words: float
    flesch: float
    grade: float
    long_sentences: int
    long_sentence_share: float
    passive_hits: int
    hedges: dict[str, int] = field(default_factory=dict)
    repeated_openers: list[tuple[str, int]] = field(default_factory=list)
    overused: list[tuple[str, int]] = field(default_factory=list)
    score: int = 0
    band: str = "unknown"
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def count_syllables(word: str) -> int:
    """Rough English syllable count used for readability formulas."""
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    if len(cleaned) <= 3:
        return 1
    groups = re.findall(r"[aeiou]+", cleaned)
    count = len(groups)
    if cleaned.endswith("e") and count > 1:
        count -= 1
    if cleaned.endswith("le") and len(cleaned) > 2 and cleaned[-3] not in "aeiou":
        count += 1
    return max(1, count)


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    return text


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    return [p.strip() for p in parts if re.search(r"[A-Za-z]", p)]


def words_of(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", text)


def analyze(text: str, max_sentence: int = 25) -> Report:
    cleaned = strip_markdown(text)
    paragraphs = [p for p in re.split(r"\n\s*\n", cleaned) if re.search(r"[A-Za-z]", p)]
    sentences = split_sentences(cleaned)
    tokens = words_of(cleaned)
    word_count = len(tokens)
    sentence_count = len(sentences) or 1
    syllables = sum(count_syllables(token) for token in tokens) or 1

    avg_sentence = word_count / sentence_count
    flesch = 206.835 - 1.015 * avg_sentence - 84.6 * (syllables / max(word_count, 1))
    grade = 0.39 * avg_sentence + 11.8 * (syllables / max(word_count, 1)) - 15.59

    sentence_lengths = [len(words_of(s)) for s in sentences]
    long_sentences = sum(1 for length in sentence_lengths if length > max_sentence)
    long_share = long_sentences / sentence_count

    passive_hits = len(_PASSIVE.findall(cleaned))

    lowered = cleaned.lower()
    hedge_counts: dict[str, int] = {}
    for hedge in HEDGES:
        found = len(re.findall(rf"\b{hedge}\b", lowered))
        if found:
            hedge_counts[hedge] = found

    opener_counts: dict[str, int] = {}
    for sentence in sentences:
        words = words_of(sentence)
        if words:
            opener = words[0].lower()
            opener_counts[opener] = opener_counts.get(opener, 0) + 1
    repeated = sorted(
        ((word, n) for word, n in opener_counts.items() if n >= 2),
        key=lambda item: (-item[1], item[0]),
    )[:5]

    content_counts: dict[str, int] = {}
    for token in tokens:
        low = token.lower()
        if len(low) > 3 and low not in STOPWORDS:
            content_counts[low] = content_counts.get(low, 0) + 1
    overused = sorted(
        ((word, n) for word, n in content_counts.items() if n >= 3),
        key=lambda item: (-item[1], item[0]),
    )[:5]

    score = flesch - 10 * long_share - min(15, passive_hits * 1.5) - min(10, sum(hedge_counts.values()))
    score = max(0, min(100, round(score)))
    band = "easy" if score >= 70 else "plain" if score >= 50 else "dense" if score >= 30 else "hard"

    suggestions: list[str] = []
    if long_sentences:
        suggestions.append(
            f"Split {long_sentences} sentence(s) longer than {max_sentence} words."
        )
    if passive_hits:
        suggestions.append(f"Rewrite {passive_hits} passive construction(s) in active voice.")
    if hedge_counts:
        total = sum(hedge_counts.values())
        suggestions.append(f"Remove or replace {total} filler/hedge word(s).")
    if repeated:
        word, n = repeated[0]
        suggestions.append(f"{n} sentence(s) start with '{word}'; vary the openings.")
    if overused:
        word, n = overused[0]
        suggestions.append(f"'{word}' appears {n} times; consider a synonym or cut it.")
    if score >= 70 and not suggestions:
        suggestions.append("Reads clearly. No structural issues detected.")

    return Report(
        words=word_count,
        sentences=len(sentences),
        paragraphs=len(paragraphs),
        syllables=syllables,
        avg_sentence_words=round(avg_sentence, 1),
        flesch=round(flesch, 1),
        grade=round(grade, 1),
        long_sentences=long_sentences,
        long_sentence_share=round(long_share, 2),
        passive_hits=passive_hits,
        hedges=hedge_counts,
        repeated_openers=repeated,
        overused=overused,
        score=score,
        band=band,
        suggestions=suggestions,
    )


def render_text(report: Report, target: str = "") -> str:
    lines = [f"plainread report{f' - {target}' if target else ''}", "=" * 50]
    lines.append(f"Score: {report.score}/100 ({report.band})")
    lines.append(f"Words: {report.words}   Sentences: {report.sentences}   Paragraphs: {report.paragraphs}")
    lines.append(f"Average sentence: {report.avg_sentence_words} words")
    lines.append(f"Flesch Reading Ease: {report.flesch}   Flesch-Kincaid grade: {report.grade}")
    lines.append(f"Long sentences: {report.long_sentences}")
    lines.append(f"Passive constructions: {report.passive_hits}")
    if report.hedges:
        hedges = ", ".join(f"{word} x{n}" for word, n in sorted(report.hedges.items()))
        lines.append(f"Hedges: {hedges}")
    if report.repeated_openers:
        openers = ", ".join(f"'{word}' x{n}" for word, n in report.repeated_openers)
        lines.append(f"Repeated sentence openers: {openers}")
    if report.overused:
        words = ", ".join(f"{word} x{n}" for word, n in report.overused)
        lines.append(f"Overused words: {words}")
    lines.append("")
    lines.append("Suggestions:")
    lines.extend(f"  - {s}" for s in report.suggestions)
    return "\n".join(lines)


def render_json(report: Report, target: str = "") -> str:
    payload = {"target": target, **report.to_dict()}
    return json.dumps(payload, indent=2)
