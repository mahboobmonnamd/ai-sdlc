#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

REQUIRED_SECTIONS = (
    "## When to use",
    "## Do not use",
    "## Required context",
    "## Stop or escalate when",
    "## Procedure",
    "## Output contract",
    "## Handoff",
)

FORBIDDEN_GENERIC_TERMS = (
    "seyal",
    "pty",
    "xcode",
    "metal renderer",
    "macos",
    "github issue",
    "make check",
)


def parse_frontmatter(text: str):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening frontmatter delimiter"
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, "missing closing frontmatter delimiter"

    data = {}
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            return None, f"invalid frontmatter line: {line!r}"
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, None


def validate_catalog(root: Path):
    errors = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return ["skills directory is missing"]

    seen = {}
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        return ["no skills found under skills/*/SKILL.md"]

    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        frontmatter, error = parse_frontmatter(text)
        label = str(path.relative_to(root))
        if error:
            errors.append(f"{label}: {error}")
            continue

        name = (frontmatter or {}).get("name", "").strip()
        description = (frontmatter or {}).get("description", "").strip()
        if not name:
            errors.append(f"{label}: frontmatter name is required")
        if not description:
            errors.append(f"{label}: frontmatter description is required")
        if name and name != path.parent.name:
            errors.append(
                f"{label}: name {name!r} must match directory {path.parent.name!r}"
            )
        if name in seen:
            errors.append(f"{label}: duplicate skill name {name!r} also used by {seen[name]}")
        elif name:
            seen[name] = label

        for section in REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{label}: missing required section {section!r}")

        lower = text.lower()
        for forbidden in FORBIDDEN_GENERIC_TERMS:
            if forbidden in lower:
                errors.append(
                    f"{label}: generic skill contains project/vendor-specific term {forbidden!r}"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate AI-SDLC skill catalog structure")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors = validate_catalog(args.root)
    if errors:
        for error in errors:
            print(f"[skill-catalog] ERROR: {error}", file=sys.stderr)
        return 1

    count = len(list((args.root / "skills").glob("*/SKILL.md")))
    print(f"[skill-catalog] valid: {count} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
