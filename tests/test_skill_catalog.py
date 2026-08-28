import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate_skills.py"
spec = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


VALID_SKILL = """---
name: example
description: Example generic skill.
---
# Example
## When to use
Use for an example.
## Do not use
Do not use elsewhere.
## Required context
Load authoritative context.
## Stop or escalate when
Stop on unresolved authority.
## Procedure
1. Inspect evidence.
## Output contract
Return a verdict.
## Handoff
Route to the next activity.
"""


class SkillCatalogTests(unittest.TestCase):
    def test_checked_in_catalog_is_valid(self):
        self.assertEqual([], module.validate_catalog(ROOT))

    def test_missing_required_section_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "example" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(VALID_SKILL.replace("## Handoff\nRoute to the next activity.\n", ""), encoding="utf-8")
            errors = module.validate_catalog(root)
            self.assertTrue(any("missing required section" in error for error in errors))

    def test_name_must_match_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "wrong-dir" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(VALID_SKILL, encoding="utf-8")
            errors = module.validate_catalog(root)
            self.assertTrue(any("must match directory" in error for error in errors))

    def test_project_specific_leakage_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "example" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(VALID_SKILL + "\nThis depends on Seyal.\n", encoding="utf-8")
            errors = module.validate_catalog(root)
            self.assertTrue(any("project/vendor-specific" in error for error in errors))

    def test_core_loop_evaluation_contract_has_coverage(self):
        contract_path = ROOT / "evals" / "core-development-loop.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        expected = {
            "development-readiness",
            "work-item-design",
            "implementation",
            "code-review",
            "verification",
            "pr-review",
        }
        scenarios = contract["scenarios"]
        covered = {scenario["skill"] for scenario in scenarios}
        self.assertEqual(expected, covered)
        for skill in expected:
            self.assertGreaterEqual(
                sum(1 for scenario in scenarios if scenario["skill"] == skill),
                2,
                f"{skill} needs at least two scenarios",
            )
        for scenario in scenarios:
            self.assertTrue(scenario["expected_behaviors"])
            self.assertTrue(scenario["forbidden_behaviors"])
        self.assertGreaterEqual(contract["scoring"]["pass_threshold"], 0.85)

    def test_pr_review_orchestrates_core_acceptance_checks(self):
        contract_path = ROOT / "evals" / "core-development-loop.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        flow = next(
            scenario
            for scenario in contract["integration_scenarios"]
            if scenario["id"] == "FLOW-001"
        )
        self.assertEqual(
            ["code-review", "verification", "risk-based-specialist-review"],
            flow["orchestrated_by_pr_review"],
        )


if __name__ == "__main__":
    unittest.main()
