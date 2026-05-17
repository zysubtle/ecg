"""Minimal CLI scaffold for the ECG RR tool.

M1 intentionally does not implement the full ECG pipeline.
"""

from __future__ import annotations

import argparse

from ecg_rr_tool import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecg-rr",
        description=(
            "Desktop ECG RR engineering analysis tool. "
            "M1 scaffold only; full analysis is implemented in later milestones."
        ),
    )
    parser.add_argument("--version", action="version", version=f"ecg-rr-tool {__version__}")
    parser.add_argument(
        "--about",
        action="store_true",
        help="Print project boundary notice and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.about:
        print("This is an engineering/research ECG analysis tool, not medical diagnostic software.")
        print("Current milestone: M1 scaffold. See docs/10_CODEX_NEXT_TASK.md for the next task.")
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
