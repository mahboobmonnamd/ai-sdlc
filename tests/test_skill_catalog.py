import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_skills", ROOT / "tools" / "validate_skills.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
eval_spec = importlib.util.spec_from_file_location("validate_eval_contracts", ROOT / "tools" / "validate_eval_contracts.py")
eval_module = importlib.util.module_from_spec(eval_spec)
eval_spec.loader.exec_module(eval_module)

PUBLIC = {"create-issue", "implement-issue", "pr-review", "process-review", "pr-merge",
          "describe-backlog", "whats-next-for-me", "projectstatus"}
SUPPORT = {"project-context", "verification"}
ROOT_SKILLS = ROOT / "skills"

class SkillCatalogTests(unittest.TestCase):
    def skill(self, name):
        return (ROOT_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

    def test_catalog_is_exact_and_structurally_valid(self):
        self.assertEqual([], module.validate_catalog(ROOT))
        self.assertEqual(PUBLIC | SUPPORT, {p.parent.name for p in ROOT_SKILLS.glob("*/SKILL.md")})

    def test_invalid_frontmatter_and_missing_sections_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "skills" / "bad" / "SKILL.md"
            p.parent.mkdir(parents=True)
            p.write_text("---\nname: bad\ndescription: No routing.\n---\n", encoding="utf-8")
            self.assertTrue(module.validate_catalog(Path(temp)))

    def test_both_implementation_gates_are_explicit(self):
        text = self.skill("implement-issue")
        for phrase in ("needs:implementation", "issue:implementing", "Gate 1", "Gate 2",
                       "origin/main", "Closes #N", "needs:review", "diffstat"):
            self.assertIn(phrase, text)
        self.assertIn("no push/PR on no", text)

    def test_review_processing_and_merge_are_separate(self):
        review = self.skill("pr-review")
        processing = self.skill("process-review")
        merge = self.skill("pr-merge")
        for term in ("[CRIT]", "[SEC]", "[NONCONF]", "[IMPR]", "[GOOD]", "REQUEST_CHANGES", "APPROVE"):
            self.assertIn(term, review)
        for term in ("should fix", "improvement", "discard", "disagree", "push back", "Apply this plan?"):
            self.assertIn(term, processing)
        self.assertIn("exact", merge)
        self.assertIn("needs:processing", review)
        self.assertIn("needs:merge", merge)

    def test_atomic_claim_is_not_implemented_using_labels_only(self):
        working = (ROOT / "docs" / "WORKING-LOOP.md").read_text(encoding="utf-8")
        for term in ("compare-and-set", "unique token", "failed or unavailable", "claim"):
            self.assertIn(term.lower(), working.lower())
        for name in ("implement-issue", "pr-review", "process-review"):
            self.assertIn("atomically", self.skill(name).lower())

    def test_dor_has_all_twelve_checks(self):
        text = (ROOT / "docs" / "WORKING-LOOP.md").read_text(encoding="utf-8")
        for term in ("Problem stated", "Observable behavior", "Bounded scope", "Verifiable acceptance",
                     "Verification command", "Design decisions closed", "Congruence", "Dependencies",
                     "Not duplicate", "Self-contained", "Implementation plan", "Security controls",
                     "!+concern"):
            self.assertIn(term, text)

    def test_all_skills_have_unit_eval_contracts(self):
        units = ROOT / "evals" / "unit"
        self.assertEqual(PUBLIC | SUPPORT, {p.stem for p in units.glob("*.json")})
        for p in units.glob("*.json"):
            self.assertEqual([], eval_module.validate_contract(p))
            c = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(p.stem, c["skill"])
            self.assertGreaterEqual(len(c["scenarios"]), 2)
            self.assertEqual("NOT_RUN", c["results"]["status"])
            for s in c["scenarios"]:
                self.assertTrue(s["expected_behaviors"])
                self.assertTrue(s["forbidden_behaviors"])
                self.assertTrue(s["scoring"]["criteria"])

    def test_implementation_uses_one_plan_gate_before_any_claim_or_branch(self):
        text = self.skill("implement-issue")
        labels = ["3. **Gate 1**", "4. **Claim**", "5. **Branch**",
                  "7. **Verification**", "8. **Gate 2**", "9. **Publish**"]
        offsets = [text.index(label) for label in labels]
        self.assertEqual(sorted(offsets), offsets)
        self.assertIn("Read-only preflight", text)
        self.assertIn("CLOSED_UNMERGED", (ROOT / "docs" / "WORKING-LOOP.md").read_text(encoding="utf-8"))
        self.assertIn("exact accepted revision", text)

    def test_previous_engineering_safeguards_remain_part_of_new_design(self):
        brief = (ROOT / "docs" / "SDLC-DESIGN.md").read_text(encoding="utf-8")
        for policy in ("Candidate continuity", "Semantic staleness", "Risk-proportional evidence",
                       "Review quality", "Merge correctness"):
            self.assertIn(policy, brief)
        self.assertIn("IN_REVIEW", self.skill("process-review"))
        self.assertIn("self-approval", self.skill("pr-review"))
        self.assertIn("conditional release", (ROOT / "docs" / "WORKING-LOOP.md").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "skills" / "whats-next-for-me" / "SKILL.md").exists())

    def test_behavioral_contracts_cover_recovery_and_revision_races(self):
        src = ROOT / "evals" / "unit"
        implementation = (src / "implement-issue.json").read_text(encoding="utf-8")
        review = (src / "pr-review.json").read_text(encoding="utf-8")
        processing = (src / "process-review.json").read_text(encoding="utf-8")
        merge = (src / "pr-merge.json").read_text(encoding="utf-8")
        self.assertIn("closed-unmerged", implementation)
        self.assertIn("Gate 1 approval", implementation)
        self.assertIn("authored PR", review)
        self.assertIn("entire accepted root-cause batch", processing)
        self.assertIn("unresolved required CI", merge)

    def test_integration_routes(self):
        path = ROOT / "evals" / "integration" / "core-development-loop.json"
        self.assertEqual([], eval_module.validate_contract(path))
        scenarios = {s["id"]: s for s in json.loads(path.read_text(encoding="utf-8"))["scenarios"]}
        self.assertEqual(["create-issue", "implement-issue", "pr-review", "pr-merge"], scenarios["FLOW-001"]["expected_route"])
        self.assertEqual(["pr-review", "process-review", "pr-review", "pr-merge"], scenarios["FLOW-002"]["expected_route"])

if __name__ == "__main__":
    unittest.main()
