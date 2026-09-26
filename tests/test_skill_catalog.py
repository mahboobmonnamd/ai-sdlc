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

EVAL_VALIDATE_PATH = ROOT / "tools" / "validate_eval_contracts.py"
eval_spec = importlib.util.spec_from_file_location(
    "validate_eval_contracts", EVAL_VALIDATE_PATH
)
eval_module = importlib.util.module_from_spec(eval_spec)
eval_spec.loader.exec_module(eval_module)

INTEGRATION_CONTRACT = ROOT / "evals" / "integration" / "core-development-loop.json"
LAYOUT_INDEX = ROOT / "evals" / "core-development-loop.json"
UNIT_DIR = ROOT / "evals" / "unit"


VALID_SKILL = """---
name: example
description: Example generic skill; not for unrelated tasks.
---
# Example
## Invocation contract
Required input: example_id.
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
            path.write_text(
                VALID_SKILL.replace(
                    "## Invocation contract\nRequired input: example_id.\n", ""
                ),
                encoding="utf-8",
            )
            errors = module.validate_catalog(root)
            self.assertTrue(any("missing required section" in error for error in errors))

    def test_description_requires_negative_routing_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "example" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                VALID_SKILL.replace(
                    "description: Example generic skill; not for unrelated tasks.",
                    "description: Example generic skill for examples."
                ),
                encoding="utf-8",
            )
            errors = module.validate_catalog(root)
            self.assertTrue(any("negative routing boundary" in error for error in errors))

    def test_name_must_match_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "wrong-dir" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(VALID_SKILL, encoding="utf-8")
            errors = module.validate_catalog(root)
            self.assertTrue(any("must match directory" in error for error in errors))

    def test_instruction_length_is_a_review_warning_not_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "example" / "SKILL.md"
            path.parent.mkdir(parents=True)
            oversized = VALID_SKILL + ("\nextra instruction" * 130)
            path.write_text(oversized, encoding="utf-8")
            self.assertEqual([], module.validate_catalog(root))
            warnings = module.collect_warnings(root)
            self.assertTrue(any("progressive-disclosure review trigger" in warning for warning in warnings))

    def test_project_specific_leakage_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "skills" / "example" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(VALID_SKILL + "\nThis depends on Seyal.\n", encoding="utf-8")
            errors = module.validate_catalog(root)
            self.assertTrue(any("project/vendor-specific" in error for error in errors))

    def test_expected_catalog_is_exact(self):
        expected = {
            "address-pr-review",
            "development-readiness",
            "implementation",
            "implementation-planning",
            "pr-review",
            "project-context",
            "verification",
            "work-item-design",
        }
        actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(expected, actual)
        self.assertNotIn("code-review", actual)

    def test_eval_contracts_validate_against_schema(self):
        self.assertEqual([], eval_module.validate_contract(LAYOUT_INDEX))
        self.assertEqual([], eval_module.validate_contract(INTEGRATION_CONTRACT))
        for path in sorted(UNIT_DIR.glob("*.json")):
            self.assertEqual([], eval_module.validate_contract(path), path)

    def test_core_eval_contract_does_not_claim_unexecuted_behavior(self):
        layout = json.loads(LAYOUT_INDEX.read_text(encoding="utf-8"))
        integration = json.loads(INTEGRATION_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual("NOT_RUN", layout["baseline"]["status"])
        self.assertEqual("NOT_RUN", layout["results"]["status"])
        self.assertEqual("NOT_RUN", integration["baseline"]["status"])
        self.assertEqual("NOT_RUN", integration["results"]["status"])
        self.assertIsNone(integration["date_last_run"])
        self.assertIn("skills_tested", integration)
        self.assertIn("target_capability", integration)

    def test_unit_contracts_match_p0_07_metadata_shape(self):
        for path in sorted(UNIT_DIR.glob("*.json")):
            contract = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.stem, contract["skill"])
            self.assertIn("fixtures", contract)
            self.assertIsInstance(contract["scoring"]["dimensions"], list)
            self.assertIn("baseline_run_date", contract["baseline"])
            self.assertIn("run_date", contract["results"])
            self.assertIn("skill_version", contract["results"])
            for scenario in contract["scenarios"]:
                self.assertEqual(scenario["id"], scenario["scenario_id"])
                self.assertIn("expected_output", scenario)
                self.assertEqual(
                    scenario["expected_behaviors"],
                    scenario["expected_output"]["required_behaviors"],
                )
                self.assertEqual(
                    scenario["forbidden_behaviors"],
                    scenario["expected_output"]["forbidden_behaviors"],
                )
                criteria = scenario["scoring"]["criteria"]
                self.assertTrue(criteria)
                for criterion in criteria:
                    self.assertIn("points", criterion)
                    self.assertTrue(criterion.get("check") or criterion.get("verification"))

    def test_planning_does_not_self_accept(self):
        planning = (
            ROOT / "skills" / "implementation-planning" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("proposed_plan_reference", planning)
        self.assertIn("plan_status: PROPOSED", planning)
        self.assertIn("Do not** update the work item's/project registry's `accepted_plan`", planning)
        self.assertNotIn("accepted_plan_reference:", planning)

    def test_exact_accepted_plan_reference_is_contractual(self):
        readiness = (
            ROOT / "skills" / "development-readiness" / "SKILL.md"
        ).read_text(encoding="utf-8")
        implementation = (
            ROOT / "skills" / "implementation" / "SKILL.md"
        ).read_text(encoding="utf-8")
        pr_review = (
            ROOT / "skills" / "pr-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("accepted_plan_reference", readiness)
        self.assertIn("accepted_by", readiness)
        self.assertIn("accepted_at", readiness)
        self.assertIn("PROPOSED", readiness)
        self.assertIn("accepted-plan reference", implementation)
        self.assertIn("accepted_by", implementation)
        self.assertIn("lifecycle_accepted_plan", pr_review)
        self.assertIn("NOT_APPLICABLE", pr_review)
        self.assertIn("REQUIRED_BUT_MISSING", pr_review)

    def test_unit_contracts_cover_every_skill(self):
        expected = {
            "address-pr-review",
            "development-readiness",
            "implementation",
            "implementation-planning",
            "pr-review",
            "project-context",
            "verification",
            "work-item-design",
        }
        actual = {path.stem for path in UNIT_DIR.glob("*.json")}
        self.assertEqual(expected, actual)
        for skill in expected:
            contract = json.loads((UNIT_DIR / f"{skill}.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(contract["scenarios"]), 2, skill)
            for scenario in contract["scenarios"]:
                self.assertTrue(scenario["expected_behaviors"])
                self.assertTrue(scenario["forbidden_behaviors"])
                self.assertTrue(scenario["scoring"]["criteria"])

    def test_normal_flow_requires_plan_acceptance_and_single_review_entrypoint(self):
        contract = json.loads(INTEGRATION_CONTRACT.read_text(encoding="utf-8"))
        flow = next(
            scenario
            for scenario in contract["scenarios"]
            if scenario["id"] == "FLOW-001"
        )
        self.assertEqual(
            [
                "work-item-design",
                "implementation-planning",
                "plan-acceptance",
                "development-readiness",
                "implementation",
                "host-project-merge-candidate",
                "pr-review",
            ],
            flow["expected_route"],
        )
        self.assertIn(
            "user must manually invoke a separate code-review skill",
            flow["forbidden_behaviors"],
        )
        self.assertIn(
            "implementation-planning self-accepts the plan",
            flow["forbidden_behaviors"],
        )

    def test_core_contract_covers_merge_candidate_and_review_gate_handoffs(self):
        unit_scenarios = {}
        for path in UNIT_DIR.glob("*.json"):
            contract = json.loads(path.read_text(encoding="utf-8"))
            for scenario in contract["scenarios"]:
                unit_scenarios[scenario["id"]] = scenario
        self.assertIn("IMPL-004", unit_scenarios)
        self.assertIn("VERIFY-003", unit_scenarios)
        self.assertIn("READY-003", unit_scenarios)
        self.assertIn("CTX-003", unit_scenarios)
        self.assertIn("IMPL-006", unit_scenarios)
        self.assertIn("PRREVIEW-005", unit_scenarios)
        self.assertIn("READY-006", unit_scenarios)

        integration = json.loads(INTEGRATION_CONTRACT.read_text(encoding="utf-8"))
        flow5 = next(
            scenario
            for scenario in integration["scenarios"]
            if scenario["id"] == "FLOW-005"
        )
        self.assertEqual(["verification", "pr-review"], flow5["expected_route"])
        flow9 = next(f for f in integration["scenarios"] if f["id"] == "FLOW-009")
        self.assertEqual(
            [
                "implementation:resume-existing-candidate",
                "implementation:complete-ci-and-scope",
                "implementation:mark-IN_REVIEW",
                "pr-review",
            ],
            flow9["expected_route"],
        )

    def test_project_context_requires_authorization_for_hosted_index(self):
        skill = (ROOT / "skills" / "project-context" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("explicit project/user authorization", skill)
        self.assertIn("non-local provider", skill)

    def test_verification_cannot_bypass_required_pr_review(self):
        skill = (ROOT / "skills" / "verification" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("does not waive any PR-review gate", skill)
        self.assertIn("do not route directly to release readiness", skill)
        self.assertIn("`IN_REVIEW` → `address-pr-review`, then full `pr-review`", skill)
        self.assertIn("`IMPLEMENTATION_IN_PROGRESS` → `implementation`", skill)
        self.assertIn("`UNKNOWN` → stop; do not guess a route", skill)

    def test_implementation_requires_concrete_candidate_before_pr_review(self):
        skill = (ROOT / "skills" / "implementation" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not invent a candidate ID", skill)
        self.assertIn("host/project creates or resolves", skill)
        self.assertIn("IMPLEMENTATION_IN_PROGRESS", skill)
        self.assertIn("IN_REVIEW", skill)

    def test_incomplete_candidate_resumes_in_implementation(self):
        contract = json.loads((UNIT_DIR / "implementation.json").read_text(encoding="utf-8"))
        scenario = next(s for s in contract["scenarios"] if s["id"] == "IMPL-005")
        self.assertIn(
            "accept the authorized IN_PROGRESS-equivalent state for resume rather than requiring the tracker label READY",
            scenario["expected_behaviors"],
        )
        self.assertIn(
            "resume implementation on the same existing candidate",
            scenario["expected_behaviors"],
        )
        integration = json.loads(INTEGRATION_CONTRACT.read_text(encoding="utf-8"))
        flow = next(
            f for f in integration["scenarios"] if f["id"] == "FLOW-007"
        )
        self.assertEqual(
            ["implementation:resume-existing-candidate", "implementation:complete", "pr-review"],
            flow["expected_route"],
        )

    def test_coordination_metadata_does_not_stale_plan(self):
        contract = json.loads(
            (UNIT_DIR / "development-readiness.json").read_text(encoding="utf-8")
        )
        scenario = next(s for s in contract["scenarios"] if s["id"] == "READY-005")
        self.assertIn(
            "treat coordination-only metadata changes as non-invalidating",
            scenario["expected_behaviors"],
        )

    def test_plan_identity_and_staleness_are_contractual(self):
        planning = (
            ROOT / "skills" / "implementation-planning" / "SKILL.md"
        ).read_text(encoding="utf-8")
        readiness = (
            ROOT / "skills" / "development-readiness" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("plan_id", planning)
        self.assertIn("plan_revision", planning)
        self.assertIn("governing_revisions", planning)
        self.assertIn("plan_id", readiness)
        self.assertIn("governing_revisions", readiness)

    def test_verification_returns_exact_revision_and_pr_review_checks_it(self):
        verification = (
            ROOT / "skills" / "verification" / "SKILL.md"
        ).read_text(encoding="utf-8")
        pr_review = (
            ROOT / "skills" / "pr-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("verified_revision", verification)
        self.assertIn("verified_revision == reviewed_revision", pr_review)
        self.assertIn("revision-sensitive evidence is stale", verification)

    def test_review_remediation_flow_is_batched_and_full(self):
        contract = json.loads(INTEGRATION_CONTRACT.read_text(encoding="utf-8"))
        flow = next(
            scenario
            for scenario in contract["scenarios"]
            if scenario["id"] == "FLOW-002"
        )
        self.assertEqual(
            ["pr-review", "address-pr-review", "pr-review"],
            flow["expected_route"],
        )
        self.assertIn("perform delta-only re-review", flow["forbidden_behaviors"])

    def test_implementation_governance_is_explicit(self):
        implementation = (
            ROOT / "skills" / "implementation" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Required argument", implementation)
        self.assertIn("work_item_id", implementation)
        self.assertIn("accepted-plan reference", implementation)
        self.assertIn("same work item + current implementer/authorized owner + implementation incomplete", implementation)
        self.assertIn("another implementer", implementation)
        self.assertIn("address-pr-review", implementation)
        self.assertIn("accepted_plan_id", implementation)
        self.assertIn("accepted_plan_revision", implementation)

    def test_readiness_requires_gap_report_when_not_ready(self):
        readiness = (
            ROOT / "skills" / "development-readiness" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("| Gap | What's missing | Proposed cure", readiness)
        self.assertIn("gap_report_body", readiness)
        self.assertIn("explicit user authorization", readiness)

    def test_pr_review_is_complete_and_standalone(self):
        pr_review = (ROOT / "skills" / "pr-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("There is no separate generic", pr_review)
        self.assertIn("all material blockers discovered in this pass", pr_review)
        self.assertIn("entire procedure again over the entire current candidate", pr_review)
        self.assertIn("address-pr-review", pr_review)
        self.assertIn("UX-008", pr_review)
        self.assertIn("NOT_APPLICABLE", pr_review)
        self.assertIn("verification_target: merge_candidate", pr_review)
        contract = json.loads(INTEGRATION_CONTRACT.read_text(encoding="utf-8"))
        self.assertNotIn("integration_scenarios", contract)

    def test_address_pr_review_requires_complete_inventory(self):
        remediation = (
            ROOT / "skills" / "address-pr-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("complete current review state", remediation)
        self.assertIn("all required-check/CI failures", remediation)
        self.assertIn("one remediation ledger", remediation)
        self.assertIn("IN_REVIEW", remediation)
        self.assertIn("RETURN_TO_IMPLEMENTATION", remediation)

    def test_schema_version_is_major_for_mandatory_plan_semantics(self):
        model = (ROOT / "phase-0" / "P0-02-context-data-model.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('version: "2.0.0"', model)
        self.assertIn('minimum_reader_version: "2.0.0"', model)
        self.assertNotIn('version: "1.1.0"', model)
        status = (ROOT / "phase-0" / "PHASE-0-STATUS-AUG-17.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("14 entity kinds, 12 relationship types", status)
        self.assertIn("Amendment — 2026-09-26", status)
        self.assertIn("2.0.0", status)
        self.assertIn("Do not invent accepted_by", model)
        self.assertIn("candidate_lifecycle_stage", model)
        resume = (ROOT / "phase-0" / "P0-05-resumability.md").read_text(encoding="utf-8")
        self.assertIn("candidate_lifecycle_stage", resume)
        self.assertIn("Never default a missing stage to `IN_REVIEW`", resume)
        rigor = (ROOT / "phase-0" / "P0-06-rigor-profiles.md").read_text(encoding="utf-8")
        self.assertIn("Plan Acceptance", rigor)
        verification = (ROOT / "skills" / "verification" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("merge_candidate_id", verification)


if __name__ == "__main__":
    unittest.main()
