import unittest

from tools.plan_acceptance import accept_plan
from tools.resume_context import (
    reconstruct_implementation_fields,
    validate_implementation_resume_context,
)

POLICY = {"technical_authorities": ["tech-lead@example.com"]}


def _context(stage="IMPLEMENTATION_IN_PROGRESS", claims=None):
    plan = {
        "id": "PLAN-WI-042",
        "status": "proposed",
        "plan_revision": 3,
        "validation_status": "current",
    }
    work_item = {"id": "WI-042"}
    accept_plan(
        work_item=work_item,
        plan=plan,
        actor="tech-lead@example.com",
        policy=POLICY,
        now="2026-09-26T12:00:00Z",
        source="decision-record:ADR-accept-3",
    )
    return {
        "policy": POLICY,
        "plans": {plan["id"]: plan},
        "work_items": {"WI-042": work_item},
        "candidates": {
            "PR-99": {
                "candidate_lifecycle_stage": stage,
                "owner": "dev-a",
                "accepted_scope_complete": stage == "IN_REVIEW",
            }
        },
        "claims": claims or {},
        "actor": "dev-a",
    }


def _checkpoint(**overrides):
    checkpoint = {
        "phase": "implementation",
        "work_item_id": "WI-042",
        "accepted_plan_id": "PLAN-WI-042",
        "accepted_plan_revision": 3,
        "merge_candidate_id": "PR-99",
        "candidate_lifecycle_stage": "IMPLEMENTATION_IN_PROGRESS",
        "actor": "dev-a",
    }
    checkpoint.update(overrides)
    return checkpoint


class ResumeContextTests(unittest.TestCase):
    def test_current_context_reconstructs_identity(self):
        context = _context()
        checkpoint = _checkpoint()
        result = validate_implementation_resume_context(checkpoint, context)
        self.assertTrue(result["ok"], result)
        fields = reconstruct_implementation_fields(checkpoint, result)
        self.assertEqual(fields["accepted_plan_revision"], 3)
        self.assertEqual(fields["candidate_lifecycle_stage"], "IMPLEMENTATION_IN_PROGRESS")

    def test_unaccepted_plan_blocks_resume(self):
        context = _context()
        context["work_items"]["WI-042"]["accepted_plan"]["operation"] = "planning-skill"
        result = validate_implementation_resume_context(_checkpoint(), context)
        self.assertEqual(result["reason"], "unaccepted_plan")

    def test_stale_plan_blocks_resume(self):
        result = validate_implementation_resume_context(
            _checkpoint(accepted_plan_revision=2), _context()
        )
        self.assertEqual(result["reason"], "stale_plan")

    def test_stage_mismatch_blocks_resume(self):
        result = validate_implementation_resume_context(
            _checkpoint(candidate_lifecycle_stage="IMPLEMENTATION_IN_PROGRESS"),
            _context("IN_REVIEW"),
        )
        self.assertEqual(result["reason"], "candidate_stage_mismatch")

    def test_unknown_stage_stops(self):
        context = _context()
        context["candidates"]["PR-99"] = {"owner": "dev-a"}
        result = validate_implementation_resume_context(
            _checkpoint(candidate_lifecycle_stage=None), context
        )
        self.assertEqual(result["reason"], "unknown_candidate_stage")

    def test_other_claim_blocks_resume(self):
        context = _context(
            claims={"WI-042": {"owner": "dev-b", "active_work_claim": "BLOCKED_BY_OTHER"}}
        )
        result = validate_implementation_resume_context(
            _checkpoint(actor="dev-a"), context
        )
        self.assertEqual(result["reason"], "blocked_by_other_claim")


if __name__ == "__main__":
    unittest.main()
