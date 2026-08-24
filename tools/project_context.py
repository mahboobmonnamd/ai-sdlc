#!/usr/bin/env python3
"""Query and validate an optional derived AI-SDLC project-context index.

The canonical SDLC context remains the project's .sdlc/context YAML workspace.
This tool only operates on a compact derived JSON navigation index.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


AUTHORITY = "derived-navigation-index"
DEFAULT_INDEX = Path(".sdlc/graph/context-index.json")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def load_index(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("context index root must be an object")
    return value


def fingerprint_value(source: dict) -> str | None:
    value = source.get("fingerprint")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if value.get("algorithm") not in {None, "git-blob-sha1"}:
            return None
        raw = value.get("value")
        return raw if isinstance(raw, str) else None
    return None


def validate(index: dict, root: Path) -> list[str]:
    errors: list[str] = []

    if index.get("authority") != AUTHORITY:
        errors.append(f"authority must be {AUTHORITY!r}")
    if not isinstance(index.get("schema_version"), str):
        errors.append("schema_version must be a string")

    nodes = index.get("nodes")
    if not isinstance(nodes, list):
        return errors + ["nodes must be a list"]

    ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            errors.append("every node must be an object")
            continue

        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            errors.append("every node must have a non-empty string id")
            continue
        ids.append(node_id)

        if not isinstance(node.get("kind"), str) or not node["kind"].strip():
            errors.append(f"{node_id}: kind is required")
        if not isinstance(node.get("summary"), str) or not node["summary"].strip():
            errors.append(f"{node_id}: summary is required")

        sources = node.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{node_id}: at least one authoritative source is required")
            continue

        for source in sources:
            if not isinstance(source, dict):
                errors.append(f"{node_id}: source must be an object")
                continue
            rel = source.get("path")
            expected = fingerprint_value(source)
            if not isinstance(rel, str) or not rel:
                errors.append(f"{node_id}: source path is required")
                continue
            if not expected:
                errors.append(
                    f"{node_id}: source {rel} requires a git-blob-sha1 fingerprint"
                )
                continue
            path = root / rel
            if not path.is_file():
                errors.append(f"{node_id}: missing source {rel}")
                continue
            actual = git_blob_sha(path)
            if actual != expected:
                errors.append(
                    f"{node_id}: stale source {rel}: index={expected} current={actual}"
                )

    seen: set[str] = set()
    for node_id in ids:
        if node_id in seen:
            errors.append(f"duplicate node id: {node_id}")
        seen.add(node_id)

    known = set(ids)
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id", "<unknown>")
        relationships = node.get("relationships", [])
        if not isinstance(relationships, list):
            errors.append(f"{node_id}: relationships must be a list")
            continue
        for relation in relationships:
            if not isinstance(relation, dict):
                errors.append(f"{node_id}: relationship must be an object")
                continue
            rel_type = relation.get("type")
            target = relation.get("target")
            if not isinstance(rel_type, str) or not rel_type:
                errors.append(f"{node_id}: relationship type is required")
            if not isinstance(target, str) or not target:
                errors.append(f"{node_id}: relationship target is required")
            elif target not in known:
                errors.append(f"{node_id}: dangling relationship target {target}")

    return errors


def searchable_text(node: dict) -> str:
    parts = [
        node.get("id", ""),
        node.get("kind", ""),
        node.get("title", ""),
        node.get("summary", ""),
    ]
    tags = node.get("tags", [])
    if isinstance(tags, list):
        parts.extend(str(tag) for tag in tags)
    return " ".join(str(part) for part in parts).lower()


def print_node(node: dict, marker: str = "match") -> None:
    print(f"{marker}: {node['id']} [{node.get('kind', '')}] — {node.get('title', '')}")
    print(f"  {node.get('summary', '')}")
    for relation in node.get("relationships", []):
        print(f"  -> {relation.get('type')}: {relation.get('target')}")
    for source in node.get("sources", []):
        print(f"  source: {source.get('path')}")


def command_validate(args: argparse.Namespace) -> int:
    try:
        index = load_index(args.index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[project-context] ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate(index, args.root)
    if errors:
        for error in errors:
            print(f"[project-context] ERROR: {error}", file=sys.stderr)
        return 1
    print(f"[project-context] valid: {len(index['nodes'])} nodes")
    return 0


def command_list(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    for node in index.get("nodes", []):
        print(f"{node['id']}\t{node.get('kind', '')}\t{node.get('title', '')}")
    return 0


def command_query(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    terms = [term.lower() for term in args.query if term.strip()]
    if not terms:
        print("query requires at least one term", file=sys.stderr)
        return 64

    scored: list[tuple[int, str, dict]] = []
    by_id = {node["id"]: node for node in index.get("nodes", []) if "id" in node}
    for node in by_id.values():
        text = searchable_text(node)
        score = sum(text.count(term) for term in terms)
        if score:
            scored.append((score, node["id"], node))
    scored.sort(key=lambda item: (-item[0], item[1]))

    if not scored:
        print(
            "[project-context] no matching nodes; search canonical .sdlc/context and authoritative repository sources"
        )
        return 2

    emitted: set[str] = set()
    for _, _, node in scored:
        if len(emitted) >= args.limit:
            break
        print_node(node, "match")
        emitted.add(node["id"])

    if args.related and len(emitted) < args.limit:
        targets: list[str] = []
        for _, _, node in scored:
            if node["id"] not in emitted:
                continue
            for relation in node.get("relationships", []):
                target = relation.get("target")
                if isinstance(target, str) and target not in emitted:
                    targets.append(target)
        for target in targets:
            if len(emitted) >= args.limit:
                break
            node = by_id.get(target)
            if node is not None and target not in emitted:
                print_node(node, "related")
                emitted.add(target)
    return 0


def command_fingerprint(args: argparse.Namespace) -> int:
    for rel in args.paths:
        path = args.root / rel
        if not path.is_file():
            print(f"missing: {rel}", file=sys.stderr)
            return 1
        print(f"{git_blob_sha(path)}  {rel}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query/validate an optional derived AI-SDLC project-context index"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--index", type=Path)
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate_parser = subcommands.add_parser("validate")
    validate_parser.set_defaults(func=command_validate)

    list_parser = subcommands.add_parser("list")
    list_parser.set_defaults(func=command_list)

    query_parser = subcommands.add_parser("query")
    query_parser.add_argument("query", nargs="+")
    query_parser.add_argument("--limit", type=int, default=8)
    query_parser.add_argument(
        "--related",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="include one-hop related nodes after direct matches",
    )
    query_parser.set_defaults(func=command_query)

    fingerprint_parser = subcommands.add_parser("fingerprint")
    fingerprint_parser.add_argument("paths", nargs="+")
    fingerprint_parser.set_defaults(func=command_fingerprint)

    args = parser.parse_args()
    args.root = args.root.resolve()
    args.index = (args.index or (args.root / DEFAULT_INDEX)).resolve()
    return args


def main() -> int:
    args = parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[project-context] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
