import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.work_claims import LocalClaimStore
from tools.workflow_claims import gate


class WorkflowClaimTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "private"
        self.db = self.root / "claims.sqlite"
        self.store = LocalClaimStore(self.db)
        self.script = Path(__file__).resolve().parents[1] / "tools" / "workflow_claims.py"

    def cli(self, action, *, phase="implement", number=10, owner="worker-a",
            file="a.token", env=None):
        args = [sys.executable, str(self.script), action, "--db", str(self.db),
                "--repo", "seyal-org/seyal", "--phase", phase,
                "--number", str(number), "--owner", owner,
                "--token-file", str(self.root / file)]
        return subprocess.run(args, text=True, capture_output=True, env=env)

    def assert_status(self, run, status, code):
        self.assertEqual(run.returncode, code, run.stderr)
        self.assertEqual(json.loads(run.stdout if code != 2 else run.stderr)["status"], status)

    def test_begin_recheck_resume_release_then_deny_replay(self):
        self.assert_status(self.cli("begin"), "ACQUIRED", 0)
        token = (self.root / "a.token").read_text()
        self.assert_status(self.cli("verify"), "VERIFIED", 0)
        self.assert_status(self.cli("begin"), "RESUMED", 0)
        self.assertEqual(token, (self.root / "a.token").read_text())
        self.assert_status(self.cli("release"), "RELEASED", 0)
        self.assertFalse((self.root / "a.token").exists())
        self.assert_status(self.cli("verify"), "DENIED", 1)
        self.assert_status(self.cli("begin", owner="worker-b", file="b.token"), "ACQUIRED", 0)
        (self.root / "a.token").write_text(token)
        os.chmod(self.root / "a.token", 0o600)
        self.assert_status(self.cli("verify"), "DENIED", 1)
        self.assert_status(self.cli("begin"), "DENIED", 1)
        self.assert_status(self.cli("release"), "DENIED", 1)

    def test_different_worker_cannot_run_or_release(self):
        self.assert_status(self.cli("begin"), "ACQUIRED", 0)
        self.assert_status(self.cli("begin", owner="worker-b", file="b.token"), "BUSY", 1)
        self.assertFalse((self.root / "b.token").exists())
        self.assert_status(self.cli("verify", owner="worker-b", file="a.token"), "DENIED", 1)
        self.assert_status(self.cli("release", owner="worker-b", file="a.token"), "DENIED", 1)
        self.assert_status(self.cli("verify"), "VERIFIED", 0)

    def test_reviewer_and_remediator_share_exclusive_pr_resource(self):
        self.assert_status(self.cli("begin", phase="review", number=88), "ACQUIRED", 0)
        self.assert_status(self.cli(
            "begin", phase="process-review", number=88, owner="fixer", file="fix.token"
        ), "BUSY", 1)
        self.assert_status(self.cli(
            "verify", phase="process-review", number=88, owner="worker-a"
        ), "VERIFIED", 0)
        self.assert_status(self.cli(
            "release", phase="review", number=88
        ), "RELEASED", 0)
        self.assert_status(self.cli(
            "begin", phase="process-review", number=88, owner="fixer", file="fix.token"
        ), "ACQUIRED", 0)

    def test_local_process_race_for_same_issue(self):
        # These subprocesses run concurrently and both enter SQLite BEGIN IMMEDIATE.
        base = [sys.executable, str(self.script), "begin", "--db", str(self.db),
                "--repo", "seyal-org/seyal", "--phase", "implement", "--number", "102"]
        a = subprocess.Popen(
            base + ["--owner", "a", "--token-file", str(self.root / "a102.token")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        b = subprocess.Popen(
            base + ["--owner", "b", "--token-file", str(self.root / "b102.token")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            ao, ae = a.communicate(timeout=20)
            bo, be = b.communicate(timeout=20)
        finally:
            if a.poll() is None:
                a.kill()
            if b.poll() is None:
                b.kill()
        self.assertEqual(sorted([a.returncode, b.returncode]), [0, 1], (ae, be))
        self.assertEqual(sorted([json.loads(ao)["status"], json.loads(bo)["status"]]),
                         ["ACQUIRED", "BUSY"])
        self.assertEqual(sum(p.exists() for p in [
            self.root / "a102.token", self.root / "b102.token"]), 1)

    def test_missing_configuration_and_token_never_authorize(self):
        env = dict(os.environ)
        env.pop("AI_SDLC_CLAIM_DB", None)
        env.pop("AI_SDLC_WORKER_ID", None)
        args = [sys.executable, str(self.script), "begin", "--repo", "seyal-org/seyal",
                "--phase", "implement", "--number", "22",
                "--token-file", str(self.root / "test.token")]
        missing = subprocess.run(args, capture_output=True, text=True, env=env)
        self.assert_status(missing, "ERROR", 2)
        self.assert_status(self.cli("verify"), "DENIED", 1)

    def test_no_token_is_exposed_in_machine_output(self):
        run = self.cli("begin")
        self.assert_status(run, "ACQUIRED", 0)
        token = (self.root / "a.token").read_text()
        self.assertNotIn(token, run.stdout)
        self.assertNotIn(token, run.stderr)
        self.assertNotIn(token, self.cli("verify").stdout)

    def test_different_issue_and_pr_numbers_do_not_conflict(self):
        self.assert_status(self.cli("begin", number=1), "ACQUIRED", 0)
        self.assert_status(self.cli("begin", number=2, owner="b", file="b.token"),
                           "ACQUIRED", 0)
        self.assert_status(self.cli("begin", phase="review", number=1, owner="c",
                                    file="c.token"), "ACQUIRED", 0)

    def test_no_silent_replacement_after_lost_token(self):
        self.assert_status(self.cli("begin"), "ACQUIRED", 0)
        (self.root / "a.token").unlink()
        self.assert_status(self.cli("begin"), "BUSY", 1)
        self.assert_status(self.cli("verify"), "DENIED", 1)
        self.assertEqual(self.store.inspect("seyal-org/seyal", "issue", 10)["status"], "HELD")


if __name__ == "__main__":
    unittest.main()
