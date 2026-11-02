#!/usr/bin/env python3
"""Claim gate for AI-SDLC worker workflows on ONE host.

The hosting agent must invoke BEGIN after read-only preflight and approval,
VERIFY before each modifying action, and RELEASE after a successful handoff
or cancellation. This is not a remote-host lock or a tool authorization layer.
All workers must share one protected local DB path.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.work_claims import (  # noqa: E402
    ClaimError, LocalClaimStore, _private_dir, _read_token_file,
    _write_token_file,
)

PHASE_KIND = {"implement": "issue", "review": "pr", "process-review": "pr"}


def gate(store: LocalClaimStore, action: str, *, repo: str, phase: str,
         number: int, owner: str, token_file: str | Path) -> dict:
    """Return a secret-free result. Never infer ownership from a GitHub label."""
    if action not in ("begin", "verify", "release") or phase not in PHASE_KIND:
        raise ClaimError("invalid workflow claim action or phase")
    path = Path(token_file).expanduser().absolute()
    _private_dir(path.parent)
    kind = PHASE_KIND[phase]
    # Inspecting another worker's claim never authorizes creating a replacement.
    exists = path.exists() or path.is_symlink()
    if action == "begin" and not exists:
        acquired = store.acquire(repo, kind, number, owner)
        if acquired["status"] != "ACQUIRED":
            return acquired
        token = acquired.pop("token")
        try:
            _write_token_file(path, token)
        except BaseException:
            # A crash between database commit and token-file creation is an
            # orphan requiring manual recovery; never auto-steal it.
            store.release(repo, kind, number, owner, token)
            raise
        if not store.recheck(repo, kind, number, owner, token):
            raise ClaimError("claim changed immediately after acquisition")
        return {"status": "ACQUIRED", "resource": acquired["resource"], "owner": owner}
    if not exists:
        return {"status": "DENIED", "reason": "missing_token_file"}
    token = _read_token_file(path)
    valid = store.recheck(repo, kind, number, owner, token)
    if not valid:
        return {"status": "DENIED", "reason": "claim_not_owned_or_stale_token"}
    if action == "begin":
        return {"status": "RESUMED", "owner": owner, "resource": store.inspect(repo, kind, number)["resource"]}
    if action == "verify":
        return {"status": "VERIFIED", "owner": owner}
    released = store.release(repo, kind, number, owner, token)
    if not released:
        return {"status": "DENIED", "reason": "claim_changed_before_release"}
    # The spent token must not prevent the worker from claiming later.
    path.unlink()
    return {"status": "RELEASED", "owner": owner}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("begin", "verify", "release"))
    parser.add_argument("--db", default=os.environ.get("AI_SDLC_CLAIM_DB"),
                        help="Same private local database for every worker on this host")
    parser.add_argument("--repo", required=True, help="Exact owner/repo")
    parser.add_argument("--phase", required=True, choices=tuple(PHASE_KIND))
    parser.add_argument("--number", required=True, type=int)
    parser.add_argument("--owner", default=os.environ.get("AI_SDLC_WORKER_ID"),
                        help="Stable, host-provided identity of this worker")
    parser.add_argument("--token-file", required=True,
                        help="Durable private token file for THIS worker and resource")
    args = parser.parse_args(argv)
    if not args.db or not args.owner:
        print(json.dumps({"status": "ERROR",
                          "reason": "configure AI_SDLC_CLAIM_DB and AI_SDLC_WORKER_ID "
                                    "(or explicit --db/--owner)"}), file=sys.stderr)
        return 2
    try:
        result = gate(LocalClaimStore(args.db), args.action,
                      repo=args.repo, phase=args.phase, number=args.number,
                      owner=args.owner, token_file=args.token_file)
        print(json.dumps(result))
        return 0 if result["status"] in ("ACQUIRED", "RESUMED", "VERIFIED", "RELEASED") else 1
    except (ClaimError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
