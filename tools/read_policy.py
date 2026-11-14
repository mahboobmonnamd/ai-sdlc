#!/usr/bin/env python3
"""Read exact top-level sections of the pinned canonical policy.

This is a read-only convenience, not an authorization or risk classifier.
No network, generated summaries, or consumer-specific dependencies.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

POLICY = Path(__file__).resolve().parents[1] / "docs" / "WORKING-LOOP.md"
HEADING = re.compile(r"^## (.+?)\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def section_id(heading: str) -> str:
    return re.sub(r"[^\w\s-]", "", heading.lower()).replace(" ", "-")


def sections(source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current = None
    lines: list[str] = []
    fence = None
    for line in source.splitlines(keepends=True):
        mark = FENCE.match(line.rstrip("\r\n"))
        if mark:
            chars, tail = mark.groups()
            if fence is None:
                fence = chars
            elif chars[0] == fence[0] and len(chars) >= len(fence) and not tail.strip():
                fence = None
        match = HEADING.match(line.rstrip("\r\n")) if fence is None and not mark else None
        if match:
            if current is not None:
                result[current] = "".join(lines)
            current = section_id(match.group(1))
            if current in result:
                raise ValueError(f"duplicate policy heading: {current}")
            lines = [line]
        elif current is not None:
            lines.append(line)
    if fence is not None:
        raise ValueError("unclosed fenced block in policy")
    if current is not None:
        result[current] = "".join(lines)
    if not result:
        raise ValueError("no policy sections found")
    return result


def select(source: str, ids: list[str]) -> str:
    available = sections(source)
    if not ids:
        raise ValueError("select at least one policy section")
    unknown = set(ids) - available.keys()
    if unknown:
        raise ValueError("unknown policy section(s): " + ", ".join(sorted(unknown)))
    # Keep source order; overlapping requests never repeat content.
    return "".join(body for name, body in available.items() if name in ids)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list available section IDs")
    parser.add_argument("sections", nargs="*")
    args = parser.parse_args(argv)
    try:
        source = POLICY.read_text(encoding="utf-8")
        if args.list:
            if args.sections:
                parser.error("--list cannot be combined with section IDs")
            print("\n".join(sections(source)))
        else:
            print(select(source, args.sections), end="")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
