import unittest

from tools.plan_acceptance import accept_plan
from tools.resume_context import (
    reconstruct_implementation_fields,
    validate_implementation_resume_context,
)

POLICY = {
    "technical_authorities": ["tech-lead@example.com"],
    "authenticators": ["host-session"],
}
PRINCIPAL = {
    "identity": "tech-lead@example.com",
    "authenticator": "host-session",
    "assertion_id": "session-accept-3",
}


def _context(stage="IMPLEMENTATION_IN_PROGRESS", claims=None, candidate=None):
    plan = {
        "id": "PLAN-WI-042",
        "work_item_id": "WI-042",
        "status": "proposed",
        "plan_revision": 3,
        "validation_status": "current",
    }
    work_item = {"id": "WI-042"}
    plans = {}
    accept_plan(
        work_item=work_item,
        plan=plan,
        plans=plans,
        principal=PRINCIPAL,
        policy=POLICY,
        now="2026-09-26T12:00:00Z",
        source="decision-record:ADR-accept-3",
    )
    if candidate is None:
        candidate = {
            "work_item_id": "WI-042",
            "candidate_lifecycle_stage": stage,
            "owner": "dev-a",
            "accepted_scope_complete": stage == "IN_REVIEW",
        }
    return {
        "policy": POLICY,
        "plans": plans,
        "work_items": {"WI-042": work_item},
        "candidates": {"PR-99": candidate},
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
        context = _context(
            candidate={"work_item_id": "WI-042", "owner": "dev-a"}
        )
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

    def test_active_claim_without_actor_fails_closed(self):
        context = _context(
            claims={"WI-042": {"owner": "dev-a", "active_work_claim": "VERIFIED"}}
        )
        context["actor"] = None
        result = validate_implementation_resume_context(
            _checkpoint(actor=None), context
        )
        self.assertEqual(result["reason"], "unknown_actor")

    def test_candidate_for_another_work_item_blocks_resume(self):
        context = _context()
        context["candidates"]["PR-99"]["work_item_id"] = "WI-OTHER"
        result = validate_implementation_resume_context(_checkpoint(), context)
        self.assertEqual(result["reason"], "candidate_work_item_mismatch")

    def test_candidate_owner_must_match_actor(self):
        context = _context()
        context["candidates"]["PR-99"]["owner"] = "dev-b"
        result = validate_implementation_resume_context(_checkpoint(), context)
        self.assertEqual(result["reason"], "candidate_owner_mismatch")


if __name__ == "__main__":
    unittest.main()
