"""Implementation-resume checks that checkpoint prose must actually call.

validate_checkpoint_for_resume() has to invoke
validate_implementation_resume_context() before it may return ready_to_resume.
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
        return {
            "ok": True,
            "reason": "not_implementation_phase",
            "accepted_plan_id": checkpoint.get("accepted_plan_id"),
            "accepted_plan_revision": checkpoint.get("accepted_plan_revision"),
            "merge_candidate_id": checkpoint.get("merge_candidate_id"),
            "candidate_lifecycle_stage": checkpoint.get("candidate_lifecycle_stage"),
        }

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
        return {
            "ok": False,
            "resumable": False,
            "reason": reason,
            "detail": verification["reason"],
            "action": "route through implementation-planning, plan acceptance, and development-readiness",
        }

    pointer = verification["accepted_plan"]
    if checkpoint.get("accepted_plan_id") != pointer["plan_id"] or checkpoint.get(
        "accepted_plan_revision"
    ) != pointer["plan_revision"]:
        return {
            "ok": False,
            "resumable": False,
            "reason": "stale_plan",
            "detail": "checkpoint plan revision is not the accepted revision",
            "action": "route through implementation-planning, plan acceptance, and development-readiness",
        }

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
    """Fields reconstruct_work_state() must copy after a passing resume check."""
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


def _resolve_candidate_stage(checkpoint: dict, context: dict) -> dict:
    candidate_id = checkpoint.get("merge_candidate_id")
    if not candidate_id:
        return {"ok": True, "candidate_lifecycle_stage": "NONE"}

    durable = (context.get("candidates") or {}).get(candidate_id) or {}
    durable_stage = durable.get("candidate_lifecycle_stage")
    checkpoint_stage = checkpoint.get("candidate_lifecycle_stage")
    if durable_stage and checkpoint_stage and durable_stage != checkpoint_stage:
        return {
            "ok": False,
            "resumable": False,
            "reason": "candidate_stage_mismatch",
            "detail": "durable candidate stage wins; checkpoint is stale",
            "candidate_lifecycle_stage": durable_stage,
            "action": "reconcile the candidate record before resume",
        }

    stage = durable_stage or checkpoint_stage
    if not stage:
        if durable.get("accepted_scope_complete") is False:
            stage = "IMPLEMENTATION_IN_PROGRESS"
        elif durable.get("accepted_scope_complete") is True and durable.get("in_review") is True:
            stage = "IN_REVIEW"
        else:
            stage = "UNKNOWN"
    if stage == "UNKNOWN":
        return {
            "ok": False,
            "resumable": False,
            "reason": "unknown_candidate_stage",
            "candidate_lifecycle_stage": "UNKNOWN",
            "action": "stop and reconcile the durable stage; do not start merge-readiness review",
        }
    return {"ok": True, "candidate_lifecycle_stage": stage}
