import unittest

from tools.plan_acceptance import accept_plan, resolve_plan_revision, verify_accepted_plan

POLICY = {
    "technical_authorities": ["tech-lead@example.com"],
    "authenticators": ["host-session"],
}
PRINCIPAL = {
    "identity": "tech-lead@example.com",
    "authenticator": "host-session",
    "assertion_id": "session-accept-3",
}


def _proposed_plan(work_item_id="WI-042", revision=3):
    return {
        "id": "PLAN-WI-042",
        "work_item_id": work_item_id,
        "status": "proposed",
        "plan_revision": revision,
        "validation_status": "current",
    }


def _accept(work_item=None, plan=None, plans=None, principal=PRINCIPAL):
    work_item = work_item if work_item is not None else {"id": "WI-042"}
    plan = plan if plan is not None else _proposed_plan()
    plans = plans if plans is not None else {}
    result = accept_plan(
        work_item=work_item,
        plan=plan,
        plans=plans,
        principal=principal,
        policy=POLICY,
        now="2026-09-26T12:00:00Z",
        source="decision-record:ADR-accept-3",
    )
    return work_item, plan, plans, result


class PlanAcceptanceTests(unittest.TestCase):
    def test_authorized_acceptance_binds_exact_revision(self):
        work_item, plan, plans, result = _accept()
        self.assertTrue(result["ok"], result)
        self.assertEqual(plan["status"], "proposed")
        stored = resolve_plan_revision(plans, "PLAN-WI-042", 3)
        self.assertEqual(stored["status"], "accepted")
        self.assertEqual(stored["work_item_id"], "WI-042")
        plans["PLAN-WI-042"]["revisions"][4] = _proposed_plan(revision=4)
        verified = verify_accepted_plan(work_item=work_item, plans=plans, policy=POLICY)
        self.assertTrue(verified["ok"], verified)
        self.assertEqual(verified["accepted_plan"]["plan_revision"], 3)

    def test_bare_identity_is_not_authority(self):
        work_item, plan, plans, result = _accept(principal="tech-lead@example.com")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "actor_not_authenticated")
        self.assertNotIn("accepted_plan", work_item)
        self.assertIsNone(resolve_plan_revision(plans, plan["id"], 3))

    def test_forged_pointer_without_host_authenticator_fails(self):
        plan = _proposed_plan()
        work_item = {
            "id": "WI-042",
            "accepted_plan": {
                "work_item_id": "WI-042",
                "plan_id": plan["id"],
                "plan_revision": 3,
                "accepted_by": "tech-lead@example.com",
                "accepted_at": "2026-09-26T12:00:00Z",
                "acceptance_source": "skill-output",
                "operation": "plan_acceptance",
            },
        }
        plans = {"PLAN-WI-042": plan}
        verified = verify_accepted_plan(work_item=work_item, plans=plans, policy=POLICY)
        self.assertFalse(verified["ok"])
        self.assertEqual(verified["reason"], "actor_not_authenticated")

    def test_plan_for_another_work_item_cannot_be_attached(self):
        work_item, _plan, _plans, result = _accept(plan=_proposed_plan("WI-099"))
        self.assertEqual(result["reason"], "plan_work_item_mismatch")
        self.assertNotIn("accepted_plan", work_item)

    def test_latest_plan_object_does_not_satisfy_an_older_acceptance(self):
        work_item, _plan, _plans, result = _accept()
        self.assertTrue(result["ok"])
        latest = _proposed_plan(revision=4)
        latest["status"] = "accepted"
        latest["accepted_revision"] = 4
        verified = verify_accepted_plan(
            work_item=work_item,
            plans={"PLAN-WI-042": latest},
            policy=POLICY,
        )
        self.assertEqual(verified["reason"], "plan_revision_unresolved")

    def test_unauthorized_identity_cannot_accept(self):
        principal = dict(PRINCIPAL, identity="planning-agent")
        _work_item, _plan, _plans, result = _accept(principal=principal)
        self.assertEqual(result["reason"], "actor_not_technical_authority")

    def test_stale_stored_revision_fails_verification(self):
        work_item, _plan, plans, result = _accept()
        self.assertTrue(result["ok"])
        plans["PLAN-WI-042"]["revisions"][3]["validation_status"] = "stale"
        verified = verify_accepted_plan(work_item=work_item, plans=plans, policy=POLICY)
        self.assertEqual(verified["reason"], "plan_stale")


if __name__ == "__main__":
    unittest.main()
