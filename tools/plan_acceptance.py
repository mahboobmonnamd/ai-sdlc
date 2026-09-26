"""Protected plan-acceptance operation.

Only accept_plan() may mark a revision accepted and advance accepted_plan.
A bare identity string is not authority: the host must pass a principal that
its authenticator already established. This module does not invent a general
capability system. It refuses unauthenticated claims and binds acceptance to
one work item and one immutable (plan_id, plan_revision) record.

Gate 4 must call verify_accepted_plan(). Non-empty evidence fields are not
authority, and the latest object stored under a plan id is not the accepted
revision.
"""

from __future__ import annotations


def accept_plan(
    *,
    work_item: dict,
    plan: dict,
    plans: dict,
    principal,
    policy: dict,
    now: str,
    source: str,
) -> dict:
    """Record one proposed revision as accepted and advance the pointer."""
    checked = _check_principal(principal, policy)
    if not checked["ok"]:
        return checked
    if plan.get("status") != "proposed":
        return _fail("plan_not_proposed")
    if plan.get("plan_revision") is None or not plan.get("id"):
        return _fail("plan_identity_missing")
    if not work_item.get("id") or plan.get("work_item_id") != work_item.get("id"):
        return _fail("plan_work_item_mismatch")
    if not now or not source:
        return _fail("acceptance_provenance_missing")

    revision = plan["plan_revision"]
    bucket = _revision_bucket(plans, plan["id"])
    if bucket is None:
        return _fail("plan_identity_not_revision_addressed")
    existing = bucket.get(revision)
    if isinstance(existing, dict) and existing.get("status") == "accepted":
        return _fail("revision_already_accepted")

    record = {
        "id": plan["id"],
        "work_item_id": work_item["id"],
        "status": "accepted",
        "plan_revision": revision,
        "accepted_revision": revision,
        "validation_status": plan.get("validation_status", "current"),
    }
    bucket[revision] = record
    identity = principal["identity"]
    pointer = {
        "work_item_id": work_item["id"],
        "plan_id": plan["id"],
        "plan_revision": revision,
        "accepted_by": identity,
        "authenticated_by": principal["authenticator"],
        "authority_assertion": principal["assertion_id"],
        "accepted_at": now,
        "acceptance_source": source,
        "operation": "plan_acceptance",
    }
    work_item["accepted_plan"] = pointer
    return {"ok": True, "accepted_plan": pointer, "accepted_revision": record}


def verify_accepted_plan(*, work_item: dict, plans: dict, policy: dict) -> dict:
    """Gate 4 check. Field presence without a host principal and exact revision fails."""
    pointer = work_item.get("accepted_plan") or None
    if not isinstance(pointer, dict):
        return _fail("accepted_plan_missing")
    if pointer.get("operation") != "plan_acceptance":
        return _fail("acceptance_not_from_protected_operation")
    if pointer.get("work_item_id") != work_item.get("id"):
        return _fail("plan_work_item_mismatch")

    claimed = {
        "identity": pointer.get("accepted_by"),
        "authenticator": pointer.get("authenticated_by"),
        "assertion_id": pointer.get("authority_assertion"),
    }
    checked = _check_principal(claimed, policy)
    if not checked["ok"]:
        return checked
    if not pointer.get("accepted_at") or not pointer.get("acceptance_source"):
        return _fail("acceptance_provenance_missing")

    record = resolve_plan_revision(plans, pointer.get("plan_id"), pointer.get("plan_revision"))
    if not isinstance(record, dict):
        return _fail("plan_revision_unresolved")
    if record.get("work_item_id") != work_item.get("id"):
        return _fail("plan_work_item_mismatch")
    if record.get("status") != "accepted":
        return _fail("plan_status_not_accepted")
    if record.get("plan_revision") != pointer.get("plan_revision"):
        return _fail("revision_mismatch")
    if record.get("accepted_revision") != pointer.get("plan_revision"):
        return _fail("acceptance_not_bound_to_revision")
    if record.get("validation_status") in ("stale", "needs_recheck", "conflicted"):
        return _fail("plan_stale")
    return {"ok": True, "reason": "accepted", "accepted_plan": pointer}


def resolve_plan_revision(plans: dict, plan_id, revision):
    """Return the immutable record for (plan_id, plan_revision), never the latest object."""
    entry = (plans or {}).get(plan_id)
    if not isinstance(entry, dict):
        return None
    revisions = entry.get("revisions")
    if not isinstance(revisions, dict):
        return None
    record = revisions.get(revision)
    if record is None and revision is not None:
        record = revisions.get(str(revision))
    return record if isinstance(record, dict) else None


def _check_principal(principal, policy: dict) -> dict:
    if isinstance(principal, str) or not isinstance(principal, dict):
        return _fail("actor_not_authenticated")
    identity = principal.get("identity")
    authenticator = principal.get("authenticator")
    assertion_id = principal.get("assertion_id")
    if not identity or not authenticator or not assertion_id:
        return _fail("actor_not_authenticated")
    allowed = set((policy or {}).get("authenticators") or [])
    if authenticator not in allowed:
        return _fail("actor_not_authenticated")
    authorities = set((policy or {}).get("technical_authorities") or [])
    if identity not in authorities:
        return _fail("actor_not_technical_authority")
    return {"ok": True}


def _revision_bucket(plans: dict, plan_id: str):
    if not isinstance(plans, dict):
        return None
    entry = plans.get(plan_id)
    if entry is None:
        entry = {"id": plan_id, "revisions": {}}
        plans[plan_id] = entry
    if not isinstance(entry, dict):
        return None
    if "revisions" not in entry and ("status" in entry or "plan_revision" in entry):
        return None
    revisions = entry.get("revisions")
    if revisions is None:
        revisions = {}
        entry["revisions"] = revisions
    if not isinstance(revisions, dict):
        return None
    return revisions


def _fail(reason: str) -> dict:
    return {"ok": False, "reason": reason}
