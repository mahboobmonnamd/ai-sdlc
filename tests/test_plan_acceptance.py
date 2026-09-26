import unittest

from tools.plan_acceptance import accept_plan, verify_accepted_plan
from tools.resume_context import (
    reconstruct_implementation_fields,
    validate_implementation_resume_context,
)


POLICY = {"technical_authorities": ["tech-lead@example.com"]}


def _proposed_plan():
    return {
        "id": "PLAN-WI-042",
        "status": "proposed",
        "plan_revision": 3,
        "validation_status": "current",
    }


class PlanAcceptanceTests(unittest.TestCase):
    def test_authorized_acceptance_is_atomic(self):
        work_item = {"id": "WI-042"}
        plan = _proposed_plan()
        result = accept_plan(
            work_item=work_item,
            plan=plan,
            actor="tech-lead@example.com",
            policy=POLICY,
            now="2026-09-26T12:00:00Z",
            source="decision-record:ADR-accept-3",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(plan["status"], "accepted")
        self.assertEqual(plan["accepted_revision"], 3)
        self.assertEqual(work_item["accepted_plan"]["operation"], "plan_acceptance")
        verified = verify_accepted_plan(
            work_item=work_item, plans={plan["id"]: plan}, policy=POLICY
        )
        self.assertTrue(verified["ok"])

    def test_forged_acceptance_fields_fail_gate(self):
        plan = _proposed_plan()
        work_item = {
            "id": "WI-042",
            "accepted_plan": {
                "plan_id": plan["id"],
                "plan_revision": 3,
                "accepted_by": "planning-agent",
                "accepted_at": "2026-09-26T12:00:00Z",
                "acceptance_source": "skill-output",
            },
        }
        verified = verify_accepted_plan(
            work_item=work_item, plans={plan["id"]: plan}, policy=POLICY
        )
        self.assertFalse(verified["ok"])
        self.assertNotEqual(verified["reason"], "accepted")
        self.assertEqual(plan["status"], "proposed")

    def test_unauthorized_actor_cannot_accept(self):
        work_item = {"id": "WI-042"}
        plan = _proposed_plan()
        result = accept_plan(
            work_item=work_item,
            plan=plan,
            actor="planning-agent",
            policy=POLICY,
            now="2026-09-26T12:00:00Z",
            source="forged",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "actor_not_technical_authority")
        self.assertNotIn("accepted_plan", work_item)
        self.assertEqual(plan["status"], "proposed")


def _ready_context(stage="IMPLEMENTATION_IN_PROGRESS"):
    plan = _proposed_plan()
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
                "accepted_scope_complete": stage == "IN_REVIEW",
            }
        },
    }


def _checkpoint(**overrides):
    checkpoint = {
        "phase": "implementation",
        "work_item_id": "WI-042",
        "accepted_plan_id": "PLAN-WI-042",
        "accepted_plan_revision": 3,
        "merge_candidate_id": "PR-99",
        "candidate_lifecycle_stage": "IMPLEMENTATION_IN_PROGRESS",
    }
    checkpoint.update(overrides)
    return checkpoint


class ResumeContextTests(unittest.TestCase):
    def test_current_context_resumes_and_reconstructs_identity(self):
        context = _ready_context()
        checkpoint = _checkpoint()
        result = validate_implementation_resume_context(checkpoint, context)
        self.assertTrue(result["ok"], result)
        fields = reconstruct_implementation_fields(checkpoint, result)
        self.assertEqual(fields["accepted_plan_id"], "PLAN-WI-042")
        self.assertEqual(fields["accepted_plan_revision"], 3)
        self.assertEqual(fields["merge_candidate_id"], "PR-99")
        self.assertEqual(fields["candidate_lifecycle_stage"], "IMPLEMENTATION_IN_PROGRESS")

    def test_unaccepted_plan_blocks_resume(self):
        plan = _proposed_plan()
        context = {
            "policy": POLICY,
            "plans": {plan["id"]: plan},
            "work_items": {
                "WI-042": {
                    "accepted_plan": {
                        "plan_id": plan["id"],
                        "plan_revision": 3,
                        "accepted_by": "tech-lead@example.com",
                        "accepted_at": "2026-09-26T12:00:00Z",
                        "acceptance_source": "forged",
                    }
                }
            },
            "candidates": {},
        }
        result = validate_implementation_resume_context(
            _checkpoint(merge_candidate_id=None, candidate_lifecycle_stage=None),
            context,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "unaccepted_plan")

    def test_stale_plan_blocks_resume(self):
        context = _ready_context()
        result = validate_implementation_resume_context(
            _checkpoint(accepted_plan_revision=2), context
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "stale_plan")

    def test_stage_mismatch_blocks_resume(self):
        context = _ready_context("IN_REVIEW")
        result = validate_implementation_resume_context(
            _checkpoint(candidate_lifecycle_stage="IMPLEMENTATION_IN_PROGRESS"),
            context,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "candidate_stage_mismatch")

    def test_unknown_stage_stops(self):
        context = _ready_context()
        context["candidates"]["PR-99"] = {}
        result = validate_implementation_resume_context(
            _checkpoint(candidate_lifecycle_stage=None),
            context,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "unknown_candidate_stage")


if __name__ == "__main__":
    unittest.main()
