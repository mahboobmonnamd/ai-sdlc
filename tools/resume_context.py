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
    "actor_not_authenticated",
    "actor_not_technical_authority",
    "acceptance_provenance_missing",
    "plan_missing",
    "plan_revision_unresolved",
    "plan_work_item_mismatch",
    "plan_status_not_accepted",
    "acceptance_not_bound_to_revision",
    "plan_identity_missing",
    "plan_identity_not_revision_addressed",
}


def validate_implementation_resume_context(checkpoint: dict, context: dict) -> dict:
    """Return ok, or a blocking reason for implementation-phase resume."""
    if checkpoint.get("phase") != "implementation":
        return _carry(checkpoint, "not_implementation_phase")

    work_item_id = checkpoint.get("work_item_id")
    work_item = (context.get("work_items") or {}).get(work_item_id) or {}
    policy = context.get("policy") or {}
    if _work_item_is_plan(work_item, policy):
        pointer = {
            "plan_id": work_item.get("id"),
            "plan_revision": work_item.get("revision", 1),
        }
    else:
        verification = verify_accepted_plan(
            work_item=work_item,
            plans=context.get("plans") or {},
            policy=policy,
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
                "fill measurable acceptance on the work item; a separate plan artifact is not required",
            )

        pointer = verification["accepted_plan"]
        if checkpoint.get("accepted_plan_id") != pointer["plan_id"] or checkpoint.get(
            "accepted_plan_revision"
        ) != pointer["plan_revision"]:
            return _block(
                "stale_plan",
                "checkpoint plan revision is not the accepted revision",
                "refresh the separate plan only when policy require_separate_plan is set",
            )

    # A lost checkpoint must reuse the one existing candidate, not open a new PR.
    # Candidate inventory is supplied by the host's fresh authoritative lookup.
    discovered = _find_existing_candidate(checkpoint, context)
    if not discovered["ok"]:
        return discovered
    checkpoint = discovered["checkpoint"]

    claim = _check_claim(checkpoint, context)
    if not claim["ok"]:
        return claim

    binding = _check_candidate_binding(checkpoint, context)
    if not binding["ok"]:
        return binding

    stage = _resolve_candidate_stage(checkpoint, context)
    if not stage["ok"]:
        return stage
    return {
        "ok": True,
        "resumable": True,
        "reason": "implementation_context_current",
        "next_action": {
            "NONE": "new_work_preflight",
            "IMPLEMENTATION_IN_PROGRESS": "resume_existing_implementation",
            "IN_REVIEW": "review_existing_candidate",
            "CLOSED_UNMERGED": "reconcile_existing_closed_candidate",
        }[stage["candidate_lifecycle_stage"]],
        "stage_advanced": stage.get("stage_advanced", False),
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


def _find_existing_candidate(checkpoint: dict, context: dict) -> dict:
    """Recover exactly one known unmerged candidate; refuse ambiguous matches."""
    work_item_id = checkpoint.get("work_item_id")
    matches = [
        cid
        for cid, candidate in (context.get("candidates") or {}).items()
        if isinstance(candidate, dict)
        and candidate.get("work_item_id") == work_item_id
        and candidate.get("merged") is not True
    ]
    if len(matches) > 1:
        return _block(
            "multiple_candidates",
            ", ".join(sorted(map(str, matches))),
            "reconcile duplicate candidates before selecting a branch or PR",
        )
    if checkpoint.get("merge_candidate_id") or not matches:
        return {"ok": True, "checkpoint": checkpoint}
    # Prior checkpoint had no candidate. The durable record is authoritative.
    # An old NONE stage must not override the recovered candidate's stage.
    return {
        "ok": True,
        "checkpoint": {
            **checkpoint,
            "merge_candidate_id": matches[0],
            "candidate_lifecycle_stage": None,
        },
    }


def _actor(checkpoint: dict, context: dict):
    return checkpoint.get("actor") or context.get("actor")


def _check_claim(checkpoint: dict, context: dict) -> dict:
    claims = context.get("claims") or {}
    claim = claims.get(checkpoint.get("work_item_id"))
    if not claim or claim.get("active_work_claim") == "NOT_APPLICABLE":
        return {"ok": True}
    owner = claim.get("owner")
    actor = _actor(checkpoint, context)
    if not owner or not actor:
        return _block(
            "unknown_actor",
            "active claim has no authenticated actor",
            "stop; do not resume without an authenticated implementer",
        )
    if owner != actor:
        return _block(
            "blocked_by_other_claim",
            owner,
            "stop; do not resume another implementer's candidate",
        )
    return {"ok": True}


def _check_candidate_binding(checkpoint: dict, context: dict) -> dict:
    candidate_id = checkpoint.get("merge_candidate_id")
    if not candidate_id:
        return {"ok": True}
    durable = (context.get("candidates") or {}).get(candidate_id)
    if not isinstance(durable, dict) or durable.get("work_item_id") != checkpoint.get("work_item_id"):
        return _block(
            "candidate_work_item_mismatch",
            candidate_id,
            "stop; the candidate is not bound to this work item",
        )
    owner = durable.get("owner")
    actor = _actor(checkpoint, context)
    if not owner or not actor:
        return _block(
            "unknown_actor",
            "candidate owner or resuming actor is missing",
            "stop; do not resume without an authenticated implementer",
        )
    if owner != actor:
        return _block(
            "candidate_owner_mismatch",
            owner,
            "stop; do not resume a candidate owned by someone else",
        )
    return {"ok": True}


def _work_item_is_plan(work_item: dict, policy: dict) -> bool:
    """The work item is the plan unless policy demands a separate artifact."""
    if (policy or {}).get("require_separate_plan"):
        return False
    criteria = work_item.get("acceptance_criteria")
    scope = work_item.get("in_scope") or work_item.get("outcome")
    return bool(criteria) and bool(scope)


def _resolve_candidate_stage(checkpoint: dict, context: dict) -> dict:
    candidate_id = checkpoint.get("merge_candidate_id")
    if not candidate_id:
        return {"ok": True, "candidate_lifecycle_stage": "NONE"}

    durable = (context.get("candidates") or {}).get(candidate_id) or {}
    if durable.get("merged") is True:
        return _block(
            "candidate_already_merged",
            candidate_id,
            "do not resume or create a replacement PR for completed work",
        )
    if durable.get("architecture_rejected") is True or durable.get("candidate_lifecycle_stage") == "REJECTED":
        return _block(
            "architecture_rejected",
            candidate_id,
            "do not resume a candidate rejected as the wrong architecture",
            candidate_lifecycle_stage="REJECTED",
        )
    if durable.get("state") == "closed":
        if durable.get("merged") is not False:
            return _block(
                "unknown_candidate_merge_status",
                candidate_id,
                "fetch the actual merged status before reopening a closed candidate",
            )
        return {"ok": True, "candidate_lifecycle_stage": "CLOSED_UNMERGED"}

    stage = durable.get("candidate_lifecycle_stage")
    if stage is None:
        if durable.get("accepted_scope_complete") is False:
            stage = "IMPLEMENTATION_IN_PROGRESS"
        elif durable.get("accepted_scope_complete") is True and durable.get("in_review") is True:
            stage = "IN_REVIEW"
    if stage not in ("IMPLEMENTATION_IN_PROGRESS", "IN_REVIEW"):
        return _block(
            "unknown_candidate_stage",
            "stage cannot be reconstructed from the durable candidate",
            "reconcile the durable stage before making another edit or PR",
            candidate_lifecycle_stage="UNKNOWN",
        )
    if stage == "IN_REVIEW" and durable.get("accepted_scope_complete") is False:
        return _block(
            "candidate_stage_inconsistent",
            "review stage contradicts incomplete accepted scope",
            "reconcile scope-completion evidence before review",
            candidate_lifecycle_stage=stage,
        )

    checkpoint_stage = checkpoint.get("candidate_lifecycle_stage")
    advanced = checkpoint_stage == "IMPLEMENTATION_IN_PROGRESS" and stage == "IN_REVIEW"
    if checkpoint_stage not in (None, "NONE", stage) and not advanced:
        return _block(
            "candidate_stage_mismatch",
            "durable candidate stage conflicts with the checkpoint",
            "reconcile a backward or incompatible transition before edits",
            candidate_lifecycle_stage=stage,
        )
    return {
        "ok": True,
        "candidate_lifecycle_stage": stage,
        "stage_advanced": advanced,
    }


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
