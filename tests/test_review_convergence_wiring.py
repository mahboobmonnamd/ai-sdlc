from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReviewConvergenceWiringTests(unittest.TestCase):
    def test_canonical_guardrails(self):
        text = (ROOT / "docs/WORKING-LOOP.md").read_text()
        for phrase in ("3 routine remediation cycles per candidate",
                       "No delta-only approval",
                       "final independent whole-candidate review on exact current head and base",
                       "never APPROVE, mark ready or merge because budget expired",
                       "Do not reset budget", "Second failed attempt"):
            self.assertIn(phrase, text)

    def test_every_mutation_or_evidence_skill_references_canonical_policy(self):
        for name in ("implement-issue", "pr-review", "process-review", "pr-merge", "verification"):
            with self.subTest(skill=name):
                text = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertIn("docs/WORKING-LOOP.md#review-convergence-and-evidence-reuse", text)

    def test_convergence_behavior_contracts_are_present_not_claimed_run(self):
        for name, ids in {
            "pr-review": {"PRREVIEW-010", "PRREVIEW-011"},
            "process-review": {"PROCESSREVIEW-005", "PROCESSREVIEW-006"},
            "implement-issue": {"IMPLEMENTISSUE-012"},
            "verification": {"VERIFICATION-003"},
            "pr-merge": {"PRMERGE-008"},
        }.items():
            with self.subTest(skill=name):
                contract = json.loads((ROOT / "evals/unit" / f"{name}.json").read_text())
                self.assertEqual("NOT_RUN", contract["results"]["status"])
                self.assertTrue(ids <= {s["id"] for s in contract["scenarios"]})

if __name__ == "__main__":
    unittest.main()
