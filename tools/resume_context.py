"""Implementation-resume checks.

validate_checkpoint_for_resume() must call
validate_implementation_resume_context() before ready_to_resume.
Candidate stage is read from durable candidate state. A missing stage is
reconstructed only when scope evidence is explicit; otherwise the result is
UNKNOWN and resume stops. Another implementer's claim blocks resume.
"""

from __future__ import annotations

from tools.plan_acceptance import verify_accepted_plan

_UNACCEPTED = {
    "accepted_plan_missing",
    "acceptance_not_from_protected_operation",
    "actor_not_technical_authority",
    "acceptance_provenance_missing",
    "plan_missing",
    "plan_status_not_accepted",
    "acceptance_not_bound_to_revision",
}


def validate_implementation_resume_context(checkpoint: dict, context: dict) -> dict:
    """Return ok, or a blocking reason for implementation-phase resume."""
    if checkpoint.get("phase") != "implementation":
        return _carry(checkpoint, "not_implementation_phase")

    work_item_id = checkpoint.get("work_item_id")
    work_item = (context.get("work_items") or {}).get(work_item_id) or {}
    verification = verify_accepted_plan(
        work_item=work_item,
        plans=context.get("plans") or {},
        policy=context.get("policy") or {},
    )
    if not verification["ok"]:
        reason = (
            "unaccepted_plan"
            if verification["reason"] in _UNACCEPTED
            else "stale_plan"
        )
        return _block(
            reason,
            verification["reason"],
            "route through implementation-planning, plan acceptance, and development-readiness",
        )

    pointer = verification["accepted_plan"]
    if checkpoint.get("accepted_plan_id") != pointer["plan_id"] or checkpoint.get(
        "accepted_plan_revision"
    ) != pointer["plan_revision"]:
        return _block(
            "stale_plan",
            "checkpoint plan revision is not the accepted revision",
            "route through implementation-planning, plan acceptance, and development-readiness",
        )

    claim = _check_claim(checkpoint, context)
    if not claim["ok"]:
        return claim

    stage = _resolve_candidate_stage(checkpoint, context)
    if not stage["ok"]:
        return stage
    return {
        "ok": True,
        "resumable": True,
        "reason": "implementation_context_current",
        "accepted_plan_id": pointer["plan_id"],
        "accepted_plan_revision": pointer["plan_revision"],
        "merge_candidate_id": checkpoint.get("merge_candidate_id"),
        "candidate_lifecycle_stage": stage["candidate_lifecycle_stage"],
    }


def reconstruct_implementation_fields(checkpoint: dict, resume_check: dict) -> dict:
    """Fields reconstruct_work_state() copies after a passing resume check."""
    return {
        "accepted_plan_id": resume_check.get("accepted_plan_id", checkpoint.get("accepted_plan_id")),
        "accepted_plan_revision": resume_check.get(
            "accepted_plan_revision", checkpoint.get("accepted_plan_revision")
        ),
        "merge_candidate_id": resume_check.get(
            "merge_candidate_id", checkpoint.get("merge_candidate_id")
        ),
        "candidate_lifecycle_stage": resume_check.get(
            "candidate_lifecycle_stage", checkpoint.get("candidate_lifecycle_stage")
        ),
    }


def _check_claim(checkpoint: dict, context: dict) -> dict:
    claims = context.get("claims") or {}
    claim = claims.get(checkpoint.get("work_item_id"))
    if not claim or claim.get("active_work_claim") == "NOT_APPLICABLE":
        return {"ok": True}
    owner = claim.get("owner")
    actor = checkpoint.get("actor") or context.get("actor")
    if owner and actor and owner != actor:
        return _block(
            "blocked_by_other_claim",
            owner,
            "stop; do not resume another implementer's candidate",
        )
    return {"ok": True}


def _resolve_candidate_stage(checkpoint: dict, context: dict) -> dict:
    candidate_id = checkpoint.get("merge_candidate_id")
    if not candidate_id:
        return {"ok": True, "candidate_lifecycle_stage": "NONE"}

    durable = (context.get("candidates") or {}).get(candidate_id) or {}
    durable_stage = durable.get("candidate_lifecycle_stage")
    checkpoint_stage = checkpoint.get("candidate_lifecycle_stage")
    if durable_stage and checkpoint_stage and durable_stage != checkpoint_stage:
        return _block(
            "candidate_stage_mismatch",
            "durable candidate stage wins; checkpoint is stale",
            "reconcile the candidate record before resume",
            candidate_lifecycle_stage=durable_stage,
        )

    stage = durable_stage or checkpoint_stage
    if not stage:
        if durable.get("accepted_scope_complete") is False:
            stage = "IMPLEMENTATION_IN_PROGRESS"
        elif durable.get("accepted_scope_complete") is True and durable.get("in_review") is True:
            stage = "IN_REVIEW"
        else:
            stage = "UNKNOWN"
    if stage == "UNKNOWN":
        return _block(
            "unknown_candidate_stage",
            "stage cannot be reconstructed",
            "stop and reconcile the durable stage; do not start merge-readiness review",
            candidate_lifecycle_stage="UNKNOWN",
        )
    return {"ok": True, "candidate_lifecycle_stage": stage}


def _carry(checkpoint: dict, reason: str) -> dict:
    return {
        "ok": True,
        "reason": reason,
        "accepted_plan_id": checkpoint.get("accepted_plan_id"),
        "accepted_plan_revision": checkpoint.get("accepted_plan_revision"),
        "merge_candidate_id": checkpoint.get("merge_candidate_id"),
        "candidate_lifecycle_stage": checkpoint.get("candidate_lifecycle_stage"),
    }


def _block(reason: str, detail: str, action: str, **extra) -> dict:
    result = {
        "ok": False,
        "resumable": False,
        "reason": reason,
        "detail": detail,
        "action": action,
    }
    result.update(extra)
    return result
