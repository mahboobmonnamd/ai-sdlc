import json
import multiprocessing
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

from tools.work_claims import ClaimError, LocalClaimStore, resource_key


def _contend(db_path, barrier, results, index):
    store = LocalClaimStore(db_path)
    barrier.wait()
    result = store.acquire("Seyal-Org/Seyal", "pr", 123, f"agent-{index}")
    results.put(result["status"])


class LocalClaimsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "claims" / "store.sqlite"
        self.store = LocalClaimStore(self.path)

    def test_claim_token_survives_restart_and_is_not_renewed_for_same_owner(self):
        original = self.store.acquire("Seyal-Org/Seyal", "issue", 17, "worker-a")
        self.assertEqual(original["status"], "ACQUIRED")
        self.assertGreaterEqual(len(original["token"]), 40)
        second = LocalClaimStore(self.path).acquire("seyal-org/seyal", "issue", 17, "worker-a")
        self.assertEqual(second["status"], "BUSY")
        self.assertNotIn("token", second)
        self.assertTrue(LocalClaimStore(self.path).recheck(
            "seyal-org/seyal", "issue", 17, "worker-a", original["token"]
        ))
        self.assertFalse(self.store.recheck("seyal-org/seyal", "issue", 17, "worker-b", original["token"]))

    def test_issue_and_pr_domains_are_separate(self):
        self.assertEqual("owner/repo:pr:5", resource_key("Owner/Repo", "pr", 5))
        self.assertEqual(self.store.acquire("owner/repo", "issue", 5, "a")["status"], "ACQUIRED")
        self.assertEqual(self.store.acquire("owner/repo", "pr", 5, "b")["status"], "ACQUIRED")
        self.assertEqual(self.store.acquire("owner/repo", "pr", 5, "reviewer")["status"], "BUSY")

    def test_conditional_release_and_token_fencing(self):
        got = self.store.acquire("owner/repo", "pr", 7, "a")
        self.assertFalse(self.store.release("owner/repo", "pr", 7, "a", "forged"))
        self.assertFalse(self.store.release("owner/repo", "pr", 7, "b", got["token"]))
        self.assertEqual(self.store.inspect("owner/repo", "pr", 7)["status"], "HELD")
        self.assertTrue(self.store.release("owner/repo", "pr", 7, "a", got["token"]))
        self.assertFalse(self.store.recheck("owner/repo", "pr", 7, "a", got["token"]))
        self.assertFalse(self.store.release("owner/repo", "pr", 7, "a", got["token"]))
        self.assertEqual(self.store.inspect("owner/repo", "pr", 7)["status"], "FREE")
        again = self.store.acquire("owner/repo", "pr", 7, "b")
        self.assertEqual(again["status"], "ACQUIRED")
        self.assertFalse(self.store.release("owner/repo", "pr", 7, "a", got["token"]))
        self.assertTrue(self.store.recheck("owner/repo", "pr", 7, "b", again["token"]))

    def test_audit_logs_actions_without_tokens(self):
        got = self.store.acquire("owner/repo", "issue", 9, "a")
        self.store.release("owner/repo", "issue", 9, "a", got["token"])
        import sqlite3
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT action FROM claim_audit ORDER BY id").fetchall()
            values = db.execute("SELECT token_hash FROM claims").fetchall()
        self.assertEqual(rows, [("ACQUIRE",), ("RELEASE",)])
        self.assertFalse(values)

    def test_two_independent_processes_have_exactly_one_winner(self):
        context = multiprocessing.get_context("spawn")
        barrier = context.Barrier(2)
        results = context.Queue()
        processes = [
            context.Process(target=_contend, args=(str(self.path), barrier, results, i))
            for i in range(2)
        ]
        for p in processes:
            p.start()
        try:
            states = [results.get(timeout=15) for _ in processes]
        finally:
            for p in processes:
                p.join(timeout=15)
                if p.is_alive():
                    p.terminate()
        self.assertTrue(all(p.exitcode == 0 for p in processes))
        self.assertEqual(sorted(states), ["ACQUIRED", "BUSY"])

    def test_reject_insecure_directory_and_database(self):
        os.chmod(self.path.parent, 0o755)
        with self.assertRaises(ClaimError):
            LocalClaimStore(self.path)
        os.chmod(self.path.parent, 0o700)
        os.chmod(self.path, 0o644)
        with self.assertRaises(ClaimError):
            LocalClaimStore(self.path)

    def test_reject_symlink_database(self):
        target = self.path.parent / "real.sqlite"
        target.touch(mode=0o600)
        fake = self.path.parent / "other.sqlite"
        fake.symlink_to(target)
        with self.assertRaises((ClaimError, OSError)):
            LocalClaimStore(fake)

    def test_invalid_resource_inputs_do_not_claim(self):
        for repo in ("", "../repo", "owner", "foo/bar/baz", "./repo"):
            with self.assertRaises(ClaimError):
                resource_key(repo, "issue", 4)
        for number in (0, -1, True):
            with self.assertRaises(ClaimError):
                resource_key("owner/repo", "issue", number)
        with self.assertRaises(ClaimError):
            resource_key("owner/repo", "review", 4)

    def test_cli_token_file_is_private_and_not_in_output(self):
        script = Path(__file__).resolve().parents[1] / "tools" / "work_claims.py"
        token_file = self.path.parent / "secret.token"
        base = [sys.executable, str(script), "--db", str(self.path)]
        target = ["--repo", "owner/repo", "--kind", "pr", "--number", "88"]
        acquire = subprocess.run(
            base + ["acquire"] + target + ["--owner", "a", "--token-file", str(token_file)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(acquire.returncode, 0, acquire.stderr)
        self.assertEqual(json.loads(acquire.stdout)["status"], "ACQUIRED")
        token = token_file.read_text(encoding="utf-8")
        self.assertNotIn(token, acquire.stdout)
        self.assertEqual(stat.S_IMODE(token_file.stat().st_mode), 0o600)
        for command, expect in (("recheck", "VERIFIED"), ("release", "RELEASED")):
            res = subprocess.run(
                base + [command] + target + ["--owner", "a", "--token-file", str(token_file)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(json.loads(res.stdout)["status"], expect)
        blocked = subprocess.run(
            base + ["acquire"] + target + ["--owner", "b", "--token-file", str(token_file)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(token_file.read_text(encoding="utf-8"), token)


if __name__ == "__main__":
    unittest.main()
