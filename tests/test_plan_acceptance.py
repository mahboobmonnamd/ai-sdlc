import unittest

from tools.plan_acceptance import accept_plan, verify_accepted_plan

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

    def test_stale_accepted_plan_fails_verification(self):
        work_item = {"id": "WI-042"}
        plan = _proposed_plan()
        accept_plan(
            work_item=work_item,
            plan=plan,
            actor="tech-lead@example.com",
            policy=POLICY,
            now="2026-09-26T12:00:00Z",
            source="decision-record:ADR-accept-3",
        )
        plan["validation_status"] = "stale"
        verified = verify_accepted_plan(
            work_item=work_item, plans={plan["id"]: plan}, policy=POLICY
        )
        self.assertFalse(verified["ok"])
        self.assertEqual(verified["reason"], "plan_stale")


if __name__ == "__main__":
    unittest.main()
