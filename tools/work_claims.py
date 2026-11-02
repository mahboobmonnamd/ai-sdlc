#!/usr/bin/env python3
"""Single-host, multi-process AI-SDLC ownership claims.

All workers MUST share one local SQLite database. This backend does not
coordinate distinct hosts/containers with independent files. No TTL or
automatic claim stealing: orphan recovery requires human intervention.
Tokens are capabilities. Never log them or pass them on a command line.
"""

from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import sys


class ClaimError(RuntimeError):
    pass


def resource_key(repo: str, kind: str, number: int) -> str:
    if (not isinstance(repo, str) or
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or
            any(part in (".", "..") for part in repo.split("/"))):
        raise ClaimError("repository must be an owner/repo identifier")
    if kind not in ("issue", "pr"):
        raise ClaimError("resource kind must be issue or pr")
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ClaimError("resource number must be positive")
    # One 'pr' key excludes both review and review-remediation agents.
    return f"{repo.casefold()}:{kind}:{number}"


def _owner(owner: str) -> str:
    if not isinstance(owner, str) or not owner.strip() or len(owner) > 256:
        raise ClaimError("owner identity is required (up to 256 characters)")
    return owner


def _token_hash(token: str) -> str:
    if not isinstance(token, str) or not token:
        raise ClaimError("claim token is missing")
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _private_dir(path: Path) -> None:
    if path.is_symlink():
        raise ClaimError("claim directory must not be a symlink")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    st = path.stat()
    if (not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or
            st.st_mode & 0o077):
        raise ClaimError("claim directory must be owned by this user and mode 0700")


def _private_file(path: Path, *, create: bool = False) -> None:
    flags = (os.O_RDWR | os.O_CREAT if create else os.O_RDONLY)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or
                st.st_mode & 0o077):
            raise ClaimError("claim/token file must be owned by this user and mode 0600")
    finally:
        os.close(fd)


class LocalClaimStore:
    """Atomic claims for processes sharing one private local database file."""

    def __init__(self, path: str | Path):
        if not hasattr(os, "getuid") or not hasattr(os, "O_NOFOLLOW"):
            raise ClaimError("local claim backend requires POSIX file security")
        self.path = Path(path).expanduser().absolute()
        _private_dir(self.path.parent)
        try:
            _private_file(self.path, create=True)
            with closing(self._connect()) as db:
                db.execute("PRAGMA journal_mode=WAL")
                db.execute("PRAGMA synchronous=FULL")
                db.execute("""CREATE TABLE IF NOT EXISTS claims (
                    resource TEXT PRIMARY KEY, owner TEXT NOT NULL,
                    token_hash TEXT NOT NULL, acquired_utc TEXT NOT NULL
                )""")
                db.execute("""CREATE TABLE IF NOT EXISTS claim_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource TEXT NOT NULL, owner TEXT NOT NULL,
                    action TEXT NOT NULL, timestamp_utc TEXT NOT NULL
                )""")
        except (OSError, sqlite3.Error) as exc:
            raise ClaimError(f"claim store unavailable: {type(exc).__name__}") from exc

    def _connect(self):
        _private_dir(self.path.parent)
        _private_file(self.path)
        return sqlite3.connect(str(self.path), timeout=5, isolation_level=None)

    @contextmanager
    def _transaction(self):
        try:
            db = self._connect()
            try:
                db.execute("BEGIN IMMEDIATE")
                yield db
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise
            finally:
                db.close()
        except sqlite3.Error as exc:
            raise ClaimError(f"claim transaction failed: {type(exc).__name__}") from exc

    def _audit(self, db, key: str, owner: str, action: str):
        db.execute(
            "INSERT INTO claim_audit(resource,owner,action,timestamp_utc) VALUES (?,?,?,?)",
            (key, owner, action, datetime.now(timezone.utc).isoformat()),
        )

    def acquire(self, repo: str, kind: str, number: int, owner: str) -> dict:
        key = resource_key(repo, kind, number)
        owner = _owner(owner)
        token = secrets.token_urlsafe(32)
        digest = _token_hash(token)
        with self._transaction() as db:
            existing = db.execute(
                "SELECT owner FROM claims WHERE resource=?", (key,)
            ).fetchone()
            if existing is not None:
                return {"status": "BUSY", "resource": key, "owner": existing[0]}
            db.execute(
                "INSERT INTO claims(resource,owner,token_hash,acquired_utc) "
                "VALUES (?,?,?,?)",
                (key, owner, digest, datetime.now(timezone.utc).isoformat()),
            )
            self._audit(db, key, owner, "ACQUIRE")
        return {"status": "ACQUIRED", "resource": key, "owner": owner, "token": token}

    def recheck(self, repo: str, kind: str, number: int, owner: str, token: str) -> bool:
        key = resource_key(repo, kind, number)
        owner = _owner(owner)
        digest = _token_hash(token)
        with self._transaction() as db:
            row = db.execute(
                "SELECT owner,token_hash FROM claims WHERE resource=?", (key,)
            ).fetchone()
        return bool(row and row[0] == owner and hmac.compare_digest(row[1], digest))

    def release(self, repo: str, kind: str, number: int, owner: str, token: str) -> bool:
        key = resource_key(repo, kind, number)
        owner = _owner(owner)
        digest = _token_hash(token)
        with self._transaction() as db:
            deleted = db.execute(
                "DELETE FROM claims WHERE resource=? AND owner=? AND token_hash=?",
                (key, owner, digest),
            ).rowcount
            if deleted:
                self._audit(db, key, owner, "RELEASE")
        return deleted == 1

    def inspect(self, repo: str, kind: str, number: int) -> dict:
        key = resource_key(repo, kind, number)
        with self._transaction() as db:
            row = db.execute(
                "SELECT owner FROM claims WHERE resource=?", (key,)
            ).fetchone()
        return {"status": "HELD" if row else "FREE",
                "resource": key, **({"owner": row[0]} if row else {})}


def _write_token_file(path: Path, token: str) -> None:
    _private_dir(path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(token)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _read_token_file(path: Path) -> str:
    _private_dir(path.parent)
    _private_file(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "r", encoding="utf-8") as stream:
        token = stream.read(512).strip()
    if not token:
        raise ClaimError("claim token file is empty")
    return token


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="One shared private local SQLite path")
    actions = parser.add_subparsers(dest="action", required=True)
    for action in ("acquire", "recheck", "release", "inspect"):
        p = actions.add_parser(action)
        p.add_argument("--repo", required=True)
        p.add_argument("--kind", required=True, choices=("issue", "pr"))
        p.add_argument("--number", required=True, type=int)
        if action != "inspect":
            p.add_argument("--owner", required=True, help="Worker identity (not a lock)")
            p.add_argument("--token-file", required=True, help="Private 0600 token file")
    args = parser.parse_args(argv)
    try:
        store = LocalClaimStore(args.db)
        if args.action == "inspect":
            result = store.inspect(args.repo, args.kind, args.number)
        elif args.action == "acquire":
            token_path = Path(args.token_file).expanduser().absolute()
            if token_path.exists() or token_path.is_symlink():
                raise ClaimError("token file already exists: refusing overwrite")
            result = store.acquire(args.repo, args.kind, args.number, args.owner)
            if result["status"] == "ACQUIRED":
                token = result.pop("token")
                try:
                    _write_token_file(token_path, token)
                except BaseException:
                    store.release(args.repo, args.kind, args.number, args.owner, token)
                    raise
                result["token_file"] = str(token_path)
        else:
            token_path = Path(args.token_file).expanduser().absolute()
            token = _read_token_file(token_path)
            held = (store.recheck(args.repo, args.kind, args.number, args.owner, token)
                    if args.action == "recheck"
                    else store.release(args.repo, args.kind, args.number, args.owner, token))
            # Remove the spent token only after the backend confirms release.
            # A rejected release must retain the secret for legitimate recovery.
            if args.action == "release" and held:
                token_path.unlink()
            result = {"status": "VERIFIED" if held else "DENIED"} if args.action == "recheck" else {
                "status": "RELEASED" if held else "DENIED"
            }
        print(json.dumps(result))
        return 0 if result["status"] not in ("DENIED", "BUSY") else 1
    except (ClaimError, OSError, sqlite3.Error) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
