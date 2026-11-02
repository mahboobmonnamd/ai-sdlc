from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillClaimWiringTests(unittest.TestCase):
    def test_implement_skill_uses_executable_gate_for_issue(self):
        body = (ROOT / "skills/implement-issue/SKILL.md").read_text()
        self.assertIn("tools/workflow_claims.py", body)
        self.assertIn("--phase implement", body)
        self.assertIn("--number", body)
        self.assertIn(" begin ", body)
        self.assertIn("verify", body)
        self.assertIn(" release ", body)
        self.assertLess(body.index("**Gate 1:**"), body.index("**Claim:**"))
        self.assertLess(body.index("**Claim:**"), body.index("**Branch:**"))

    def test_review_and_remediation_share_real_pr_claim(self):
        review = (ROOT / "skills/pr-review/SKILL.md").read_text()
        process = (ROOT / "skills/process-review/SKILL.md").read_text()
        for body, phase in ((review, "review"), (process, "process-review")):
            self.assertIn("tools/workflow_claims.py", body)
            self.assertIn(f"--phase {phase}", body)
            self.assertIn(" begin ", body)
            self.assertIn("verify", body)
            self.assertIn(" release ", body)
        self.assertLess(process.index("**Single gate:**"),
                        process.index("**Claim after approval, then edit:**"))

    def test_reference_adapter_requires_one_db_and_explicit_host_owner(self):
        docs = (ROOT / "docs/WORKING-LOOP.md").read_text()
        self.assertIn("AI_SDLC_CLAIM_DB", docs)
        self.assertIn("AI_SDLC_WORKER_ID", docs)
        self.assertIn("AI_SDLC_CLAIM_TOKEN_FILE", docs)
        self.assertIn("AI_SDLC_TOOL_ROOT", docs)
        self.assertIn("per-worktree DB", docs)
        self.assertIn("does **not authenticate identities**", docs)
        self.assertIn("unique across concurrently active workers", docs)
        self.assertIn("Re-verify immediately before", docs)


if __name__ == "__main__":
    unittest.main()
