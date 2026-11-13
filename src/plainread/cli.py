"""Command line interface for plainread."""

from __future__ import annotations

import argparse
import sys

from . import analyze, render_json, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plainread",
        description="Score the readability of a Markdown or text file and list concrete fixes.",
    )
    parser.add_argument("path", nargs="?", help="file to read; use '-' for stdin (default: stdin)")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--out", help="also write the report to this path")
    parser.add_argument("--max-sentence", type=int, default=25,
                        help="word count above which a sentence is reported (default 25)")
    parser.add_argument("--fail-under", type=int, default=0,
                        help="exit with status 1 when the score is below this value (default 0 = never)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.path and args.path != "-":
            with open(args.path, "r", encoding="utf-8") as handle:
                text = handle.read()
            target = args.path
        else:
            text = sys.stdin.read()
            target = "<stdin>"
    except OSError as exc:
        print(f"plainread: {exc}", file=sys.stderr)
        return 2

    if not text.strip():
        print("plainread: no text to analyse", file=sys.stderr)
        return 2

    report = analyze(text, args.max_sentence)
    output = render_json(report, target) if args.json else render_text(report, target)
    print(output)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(output + "\n")

    if args.fail_under and report.score < args.fail_under:
        print(
            f"plainread: score {report.score} is below required {args.fail_under}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
