from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "docs/WORKING-LOOP.md#desktop-safe-test-execution"


class DesktopTestPolicyTests(unittest.TestCase):
    def test_all_execution_capable_workflow_skills_reference_policy(self):
        for name in ("implement-issue", "verification", "pr-review",
                     "process-review", "pr-merge"):
            with self.subTest(skill=name):
                body = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertIn(ANCHOR, body)
                self.assertIn("explicit per-run human authorization", body)
                self.assertIn("Never self-authorize", body)
                self.assertIn("NOT_RUN / INCONCLUSIVE", body)
                self.assertLess(body.index("## Desktop-safe testing"),
                                body.index("## Procedure"))

    def test_normative_policy_preserves_isolation_and_evidence(self):
        body = (ROOT / "docs/WORKING-LOOP.md").read_text()
        policy = body.split("## Desktop-safe test execution", 1)[1].split(
            "## Verification and merge", 1)[0]
        for required in ("Non-disruptive by default", "transitive scripts",
                         "explicit per-run human authorization", "generic CI flag",
                         "fail closed", "serialize exclusive desktop use",
                         "bound execution and retries", "test-owned resources",
                         "Required evidence remains a review/merge gate",
                         "not an OS-level sandbox", "never claim a previous run executed",
                         "new interactive permission", "three-cycle/early-stop policy",
                         "no duplicate invocation", "fresh authorization"):
            self.assertIn(required, policy)
        adapter = (ROOT / "docs/CONSUMER-ABSORPTION.md").read_text()
        self.assertIn("WORKING-LOOP.md#desktop-safe-test-execution", adapter)
        self.assertIn("fail closed before disruptive effects", adapter)
        self.assertIn("review-convergence-and-evidence-reuse", adapter)
        self.assertIn("VERIFICATION-003", {s["id"] for s in json.loads(
            (ROOT / "evals/unit/verification.json").read_text())["scenarios"]})

    def test_behavioral_scenarios_remain_unrun_until_exercised(self):
        contract = json.loads((ROOT / "evals/unit/verification.json").read_text())
        scenarios = {s["id"]: s for s in contract["scenarios"]}
        for number, verdict in ((4, "INCONCLUSIVE"), (5, "VERIFIED"),
                                (6, "INCONCLUSIVE"), (7, "VERIFIED"),
                                (8, "INCONCLUSIVE"), (9, "INCONCLUSIVE")):
            row = scenarios[f"VERIFICATION-{number:03}"]
            self.assertEqual(f"output.verdict == {verdict}",
                             row["scoring"]["criteria"][0]["check"])
            self.assertTrue(row["forbidden_behaviors"])
        self.assertEqual("NOT_RUN", contract["results"]["status"])


if __name__ == "__main__":
    unittest.main()
