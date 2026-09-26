---
name: address-pr-review
description: Remediate all known review findings/check failures on one existing merge candidate already in review; not for unfinished feature implementation or final merge-readiness review.
---

# Address PR review

## Invocation contract

Required argument:

```text
merge_candidate_id: authoritative PR/MR/change-list identifier
```

For hosts that expose numeric pull-request identifiers, the consumer facade may name this argument `pr_number`. Do not infer a different merge candidate from a nearby work item when the requested review target is explicit.

Requests such as “address PR comments”, “fix reviewer feedback”, “resolve review findings”, or “fix the failing checks on this PR” route here **only when** the candidate is already in review stage (`candidate_lifecycle_stage = IN_REVIEW`). If implementation of the accepted scope is still incomplete, keep remediation under `implementation` instead.

This skill remains independently usable (PRD UX-008) for review-stage candidates that have no AI-SDLC work-item/plan binding.

## When to use

Use only when an existing merge candidate is in **review stage** and has review feedback, unresolved review threads, required-check failures, or a prior `pr-review` verdict that requires implementation/test/evidence-generation changes.

## Do not use

- Do not start new feature implementation unrelated to the reviewed candidate.
- Do not use this skill as the primary route while accepted-scope implementation is still incomplete (`IMPLEMENTATION_IN_PROGRESS`); stay in `implementation`.
- Do not fix only the latest comment while older material findings remain unresolved.
- Do not treat resolved-thread UI state as proof the underlying defect is fixed.
- Do not weaken tests, checks, or acceptance criteria merely to make the candidate green.
- Do not perform the final merge-readiness review here.
- Do not create a second branch/merge candidate for the same remediation unless project policy explicitly requires it.
- Do not silently resolve product/architecture/security/compliance decisions in remediation.

## Lifecycle context (conditional)

Resolve optional lifecycle bindings with the same labels as `pr-review`:

```text
lifecycle_work_item: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
lifecycle_accepted_plan: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
```

Enforce an accepted plan only when project policy or the owning workflow requires one (`REQUIRED_*` / `AVAILABLE`). When `NOT_APPLICABLE`, remediate against candidate intent, repository authority, tests/checks, and applicable requirements. When `REQUIRED_BUT_MISSING`, stop with `BLOCKED` / inconclusive rather than inventing a plan.

## Required context

Load:

- exact merge-candidate identifier, base, and current immutable revision when available;
- `candidate_lifecycle_stage` (`IMPLEMENTATION_IN_PROGRESS` | `IN_REVIEW` | `UNKNOWN`);
- lifecycle work-item/plan context states above; when `AVAILABLE`, the owning work item and accepted implementation plan with acceptance evidence;
- **complete** unresolved review-thread/comment set, including older threads;
- prior `pr-review` findings and their dispositions;
- all required checks/CI and any current failures;
- governing requirements/decisions/specifications when available;
- affected production code/tests and applicable specialist evidence;
- project rules for who may push/update the candidate.

Treat the latest comment as one input, never as the whole remediation scope.

## Stop or escalate when

Stop and route rather than editing when:

- the merge candidate does not exist or is closed/merged;
- the current actor is not authorized to modify the candidate;
- `candidate_lifecycle_stage` is `IMPLEMENTATION_IN_PROGRESS` or implementation of accepted scope is otherwise incomplete → route to `implementation`;
- `candidate_lifecycle_stage` is `UNKNOWN` → stop and reconcile the durable stage (`status: BLOCKED`, `next_action: reconcile-candidate-stage`); do not remediate, and do not route to `implementation` or `pr-review`;
- the candidate revision changes while the remediation inventory is being built and the inventory can no longer be trusted;
- a finding requires a new product/architecture/security/compliance decision;
- remediation would materially expand the owning work item's accepted scope (when a work item applies);
- an unresolved finding belongs to a different ownership boundary and cannot be safely fixed in this candidate;
- the review feedback is contradictory and authority cannot resolve it;
- lifecycle plan context is `REQUIRED_BUT_MISSING`;
- the only way to satisfy feedback is to weaken valid acceptance or evidence.

## Procedure

1. Resolve `merge_candidate_id`, record the current revision, modification authority, and `candidate_lifecycle_stage`. If stage is `UNKNOWN`, stop and reconcile the durable stage before any remediation or handoff to `implementation` or `pr-review`. If stage is `IMPLEMENTATION_IN_PROGRESS` (or accepted-scope work is incomplete), stop and hand off to `implementation` without performing merge-readiness remediation.
2. Classify lifecycle work-item/plan context (`AVAILABLE` | `NOT_APPLICABLE` | `REQUIRED_BUT_MISSING`). When `REQUIRED_BUT_MISSING`, stop blocked/inconclusive. When `AVAILABLE`, load the accepted plan at the exact revision. When `NOT_APPLICABLE`, proceed without a plan.
3. Fetch the **complete current review state**: unresolved review threads/comments, prior blocking findings, and all required-check/CI failures. Do not stop after the newest comment.
4. Build one remediation ledger:
   ```text
   item -> source -> root cause -> affected surface -> planned correction -> required proof
   ```
   Group duplicate symptoms under one root cause while preserving independent blockers.
5. Reconcile feedback against authoritative scope/candidate intent. Mark comments that are already resolved by current code, superseded, non-blocking, or authority-conflicting; do not blindly implement every suggestion.
6. For every in-scope material blocker, fix the **root cause**, not merely the cited line. Search the approved change surface for sibling occurrences of the same defect pattern/invariant.
7. Keep remediation bounded to the reviewed candidate and review findings. Record unrelated cleanup separately. Do not expand unfinished feature scope here.
8. Run the narrowest relevant check after each root-cause fix, then run all candidate-required checks affected by the remediation.
9. Re-fetch the review/check state and reconcile every ledger row. Do not request re-review while a known material row remains unresolved unless it is explicitly blocked with evidence.
10. Re-resolve the exact candidate revision. If it moved unexpectedly, re-check the remediation ledger against the current candidate before handoff.
11. Hand off by stage:
    - `IN_REVIEW` → hand the **entire current candidate** to `pr-review` (full review; prior findings are a regression checklist).
    - If stage is discovered to still be `IMPLEMENTATION_IN_PROGRESS` after bounded check/feedback fixes → return to `implementation`, **not** full merge-readiness `pr-review`.
    - If stage is `UNKNOWN` → stop with `reconcile-candidate-stage`; do not hand off to `implementation` or `pr-review`.

## Output contract

Return:

```text
merge_candidate_id
starting_revision
ending_revision
candidate_lifecycle_stage: IMPLEMENTATION_IN_PROGRESS | IN_REVIEW | UNKNOWN
lifecycle_work_item: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
lifecycle_accepted_plan: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
remediation_ledger:
  - finding_or_check
    source
    root_cause
    affected_surface
    status: RESOLVED | STILL_OPEN | BLOCKED | SUPERSEDED_WITH_REASON
    proof
checks_run_and_results
scope_assessment
new_authority_or_scope_gaps
unknowns
status: READY_FOR_FULL_REREVIEW | RETURN_TO_IMPLEMENTATION | BLOCKED
next_action: pr-review | implementation | decision-activity | reconcile-candidate-stage | BLOCKED
```

`READY_FOR_FULL_REREVIEW` requires every known material review/check item to be resolved or explicitly blocked and reported, and the candidate stage to be `IN_REVIEW`.

## Handoff

- `IN_REVIEW` and all known material findings/check failures reconciled → `pr-review` on the full current candidate.
- `IMPLEMENTATION_IN_PROGRESS` or incomplete accepted-scope work → `implementation` (even if CI/feedback was touched); do not enter full merge-readiness `pr-review` yet.
- `UNKNOWN` → stop and reconcile the durable stage. Do not remediate, and do not hand off to `implementation` or `pr-review`.
- Authority/scope decision required → corresponding decision/work-item activity, then readiness before further production changes when a work item applies.
- Candidate missing/closed/merged → stop; do not create a replacement implementation path automatically.
- New unrelated work discovered → record a separate work item; do not expand this remediation candidate.
