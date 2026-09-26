---
name: implementation
description: Implement a ready work item or resume its authorized in-progress candidate from the accepted plan; not for PR-review remediation or another developer's active candidate.
---

# Implementation

## Invocation contract

Required argument:

```text
work_item_id: authoritative tracker/work-item identifier
```

Optional when already known:

```text
merge_candidate_id: existing PR/MR/change-list for this same work item
```

Use this for new implementation and for continuing incomplete implementation on the same authorized merge candidate. Review-comment/check remediation belongs to `address-pr-review`.

## When to use

Use for NEW work when the work item is READY, or for RESUME when the same authorized implementer already owns an in-progress candidate and the prior readiness inputs remain current. In both modes the accepted plan must still be current.

## Do not use

- Do not invent product/architecture decisions, broaden scope, weaken tests, or add disposable production paths.
- Do not create a second implementation path when a candidate already exists.
- Do not use this skill when the requested work is reviewer-feedback/check remediation; use `address-pr-review`.
- Do not continue another implementer's candidate without an explicit project ownership handoff.

## Required context

Load the work item, accepted implementation-plan identity/revision, governing authority, acceptance criteria, relevant code/tests, required evidence/risk gates, ownership policy, and merge-candidate state/ownership when one exists.

## Implementation governance preflight

Before branch/worktree/files/production edits:

1. Fresh-read `work_item_id`; require it to be open/current (not closed/cancelled/blocked by unresolved authority).
2. Check fresh ownership/claim state. If another implementer owns the work item or candidate, stop.
3. Resolve open merge candidates for this work item and determine mode:
   - none → `NEW`; require the work-item state to be READY before implementation starts;
   - same work item + current implementer/authorized owner + implementation incomplete → `RESUME_EXISTING_CANDIDATE`; an IN_PROGRESS-equivalent tracker state is valid and must not be rejected merely because it is no longer labeled READY;
   - same candidate + request is reviewer feedback or required-check remediation → route to `address-pr-review`;
   - candidate owned by another implementer or ownership is ambiguous → stop;
   - multiple active candidates for the same work item → stop and reconcile; never create another.
4. Resolve the work item's/project registry's accepted-plan reference, then load immutable content for that exact `plan_id + plan_revision`; if the exact revision cannot be resolved, stop instead of falling back to latest. Require it to be current for its planning-relevant governing revisions. Do not select an arbitrary related/latest plan. On RESUME, also revalidate acceptance/dependencies/authority so prior readiness has not gone stale.
5. If the project defines exclusive claiming, acquire/verify it for NEW work or re-verify it when RESUMING.

If the project defines no claim mechanism, do not invent one.

## Stop or escalate when

Stop for missing/ambiguous/closed work item, NEW work that is not READY, stale resume prerequisites, missing/stale plan, ownership collision, ambiguous/multiple candidates, scope/authority conflict, missing dependency, untestable acceptance, material feasibility unknown, or a required temporary/parallel production path.

## Procedure

1. Run the governance preflight and record whether this is `NEW` or `RESUME_EXISTING_CANDIDATE`.
2. Reconstruct the accepted scope and exact accepted plan revision; do not silently revise either.
3. Identify the smallest evidence/test that would fail before the intended behavior exists.
4. Implement the smallest coherent permanent production change on the authorized branch/candidate.
5. Preserve unrelated behavior; record unrelated defects separately.
6. Exercise applicable failure/boundary behavior, not only the happy path.
7. Run narrow checks continuously, then all project-required checks for this work.
8. Record exact proof for claimed success; write `unknown` rather than inventing evidence.
9. If implementation exposes a material authority/design fork or makes the plan stale, stop and route backward.
10. When implementation is complete, keep using the existing candidate if one exists; otherwise let host/project policy create or resolve the concrete candidate. Do not invent a candidate ID.

## Output contract

```text
work_item_id
status: IMPLEMENTED_FOR_REVIEW | IN_PROGRESS | BLOCKED | RETURN_TO_DECISION | NEEDS_SPIKE
implementation_mode: NEW | RESUME_EXISTING_CANDIDATE
accepted_plan_id
accepted_plan_revision
implementation_plan: CONFIRMED | MISSING | STALE
merge_candidate: NONE | OPEN:<id> | UNKNOWN
merge_candidate_ownership: CURRENT_IMPLEMENTER | OTHER_IMPLEMENTER | UNKNOWN | NOT_APPLICABLE
active_work_claim: NOT_APPLICABLE | VERIFIED_CURRENT_IMPLEMENTER | BLOCKED_BY_OTHER | CLAIM_FAILED
implemented_scope
changed_surfaces
tests_or_evidence_added
checks_run_and_results
proof
unknowns
new_risks_or_decisions_discovered
next_action
```

## Handoff

- Incomplete implementation on authorized existing candidate → remain in `implementation` on that same candidate.
- Completed implementation with existing candidate → `pr-review <merge_candidate_id>`.
- Completed implementation without candidate → host/project creates or resolves the candidate, then `pr-review`.
- Existing candidate with reviewer feedback/check failures → `address-pr-review`.
- Missing/stale plan → `implementation-planning` (or `work-item-design` if scope/acceptance is weak), then `development-readiness`.
- Authority/scope/feasibility problem → appropriate upstream decision/design/spike, then readiness again.
