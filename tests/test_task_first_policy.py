from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "docs/WORKING-LOOP.md#task-first-execution-and-progressive-context"


class TaskFirstPolicyTests(unittest.TestCase):
    def test_active_skills_route_to_task_first_policy(self):
        for name in ("create-issue", "implement-issue", "pr-review",
                     "process-review", "pr-merge", "verification", "project-context"):
            with self.subTest(skill=name):
                body = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertIn(ANCHOR, body)

    def test_policy_preserves_protections_and_reduces_repeat_work(self):
        body = (ROOT / "docs/WORKING-LOOP.md").read_text()
        for phrase in ("LIGHTWEIGHT", "STANDARD", "CRITICAL",
                       "independent exact-head approval", "branch protections",
                       "Unknown risk", "no second review",
                       "A review may find zero issues", "one compact, durable candidate record",
                       "do not preload this entire document"):
            self.assertIn(phrase, body)

    def test_new_behavioral_cases_not_claimed_run(self):
        for name, ids in {
            "create-issue": {"CREATEISSUE-003"},
            "implement-issue": {"IMPLEMENTISSUE-013"},
            "pr-review": {"PRREVIEW-012", "PRREVIEW-013"},
            "project-context": {"PROJECTCONTEXT-003"},
        }.items():
            contract = json.loads((ROOT / "evals" / "unit" / f"{name}.json").read_text())
            self.assertTrue(ids <= {s["id"] for s in contract["scenarios"]})
            self.assertEqual("NOT_RUN", contract["results"]["status"])


if __name__ == "__main__":
    unittest.main()
