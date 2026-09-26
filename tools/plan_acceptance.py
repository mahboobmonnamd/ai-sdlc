"""Protected plan-acceptance operation.

accepted_plan, accepted_by, accepted_at, and plan status=accepted are not
ordinary skill writes. Only accept_plan() may set them, and only after the
actor is in the project technical-authority policy. Gate 4 must call
verify_accepted_plan(); non-empty evidence fields are not authority.
"""

from __future__ import annotations


def accept_plan(
    *,
    work_item: dict,
    plan: dict,
    actor: str,
    policy: dict,
    now: str,
    source: str,
) -> dict:
    """Atomically mark one proposed revision accepted and advance the pointer."""
    authorities = set(policy.get("technical_authorities") or [])
    if not actor or actor not in authorities:
        return {"ok": False, "reason": "actor_not_technical_authority"}
    if plan.get("status") != "proposed":
        return {"ok": False, "reason": "plan_not_proposed"}
    if plan.get("plan_revision") is None or not plan.get("id"):
        return {"ok": False, "reason": "plan_identity_missing"}
    if not now or not source:
        return {"ok": False, "reason": "acceptance_provenance_missing"}

    revision = plan["plan_revision"]
    plan["status"] = "accepted"
    plan["accepted_revision"] = revision
    pointer = {
        "plan_id": plan["id"],
        "plan_revision": revision,
        "accepted_by": actor,
        "accepted_at": now,
        "acceptance_source": source,
        "operation": "plan_acceptance",
    }
    work_item["accepted_plan"] = pointer
    return {"ok": True, "accepted_plan": pointer}


def verify_accepted_plan(*, work_item: dict, plans: dict, policy: dict) -> dict:
    """Gate 4 check. Field presence without authority and status=accepted fails."""
    pointer = work_item.get("accepted_plan") or None
    if not isinstance(pointer, dict):
        return _fail("accepted_plan_missing")
    if pointer.get("operation") != "plan_acceptance":
        return _fail("acceptance_not_from_protected_operation")

    actor = pointer.get("accepted_by")
    authorities = set(policy.get("technical_authorities") or [])
    if not actor or actor not in authorities:
        return _fail("actor_not_technical_authority")
    if not pointer.get("accepted_at") or not pointer.get("acceptance_source"):
        return _fail("acceptance_provenance_missing")

    plan = plans.get(pointer.get("plan_id"))
    if not isinstance(plan, dict):
        return _fail("plan_missing")
    if plan.get("status") != "accepted":
        return _fail("plan_status_not_accepted")
    if plan.get("plan_revision") != pointer.get("plan_revision"):
        return _fail("revision_mismatch")
    if plan.get("accepted_revision") != pointer.get("plan_revision"):
        return _fail("acceptance_not_bound_to_revision")
    if plan.get("validation_status") in ("stale", "needs_recheck", "conflicted"):
        return _fail("plan_stale")
    return {"ok": True, "reason": "accepted", "accepted_plan": pointer}


def _fail(reason: str) -> dict:
    return {"ok": False, "reason": reason}
