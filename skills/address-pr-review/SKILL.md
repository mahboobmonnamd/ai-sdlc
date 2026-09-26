---
name: address-pr-review
description: Remediate all known review findings/check failures on one existing merge candidate; not for unfinished feature implementation or final merge-readiness review.
---

# Address PR review

## Invocation contract

Required argument:

```text
merge_candidate_id: authoritative PR/MR/change-list identifier
```

For hosts that expose numeric pull-request identifiers, the consumer facade may name this argument `pr_number`. Do not infer a different merge candidate from a nearby work item when the requested review target is explicit.

Requests such as “address PR comments”, “fix reviewer feedback”, “resolve review findings”, or “fix the failing checks on this PR” route here, not to `implementation`.

## When to use

Use only when an existing merge candidate has review feedback, unresolved review threads, required-check failures, or a prior `pr-review` verdict that requires implementation/test/evidence-generation changes.

## Do not use

- Do not start new feature implementation unrelated to the reviewed candidate.
- Do not fix only the latest comment while older material findings remain unresolved.
- Do not treat resolved-thread UI state as proof the underlying defect is fixed.
- Do not weaken tests, checks, or acceptance criteria merely to make the candidate green.
- Do not perform the final merge-readiness review here.
- Do not create a second branch/merge candidate for the same remediation unless project policy explicitly requires it.
- Do not silently resolve product/architecture/security/compliance decisions in remediation.

## Required context

Load:

- exact merge-candidate identifier, base, and current immutable revision when available;
- owning work item and accepted implementation plan;
- **complete** unresolved review-thread/comment set, including older threads;
- prior `pr-review` findings and their dispositions;
- all required checks/CI and any current failures;
- governing requirements/decisions/specifications;
- affected production code/tests and applicable specialist evidence;
- project rules for who may push/update the candidate.

Treat the latest comment as one input, never as the whole remediation scope.

## Stop or escalate when

Stop and route rather than editing when:

- the merge candidate does not exist or is closed/merged;
- the current actor is not authorized to modify the candidate;
- the candidate revision changes while the remediation inventory is being built and the inventory can no longer be trusted;
- a finding requires a new product/architecture/security/compliance decision;
- remediation would materially expand the owning work item's accepted scope;
- an unresolved finding belongs to a different ownership boundary and cannot be safely fixed in this candidate;
- the review feedback is contradictory and authority cannot resolve it;
- the only way to satisfy feedback is to weaken valid acceptance or evidence.

## Procedure

1. Resolve `merge_candidate_id`, record the current revision, owning work item, and modification authority.
2. Fetch the **complete current review state**: unresolved review threads/comments, prior blocking findings, and all required-check/CI failures. Do not stop after the newest comment.
3. Build one remediation ledger:
   ```text
   item -> source -> root cause -> affected surface -> planned correction -> required proof
   ```
   Group duplicate symptoms under one root cause while preserving independent blockers.
4. Reconcile feedback against authoritative scope. Mark comments that are already resolved by current code, superseded, non-blocking, or authority-conflicting; do not blindly implement every suggestion.
5. For every in-scope material blocker, fix the **root cause**, not merely the cited line. Search the approved change surface for sibling occurrences of the same defect pattern/invariant.
6. Keep remediation bounded to the owning work item and review findings. Record unrelated cleanup separately.
7. Run the narrowest relevant check after each root-cause fix, then run all candidate-required checks affected by the remediation.
8. Re-fetch the review/check state and reconcile every ledger row. Do not request re-review while a known material row remains unresolved unless it is explicitly blocked with evidence.
9. Re-resolve the exact candidate revision. If it moved unexpectedly, re-check the remediation ledger against the current candidate before handoff.
10. Hand the **entire current candidate** to `pr-review`. The next review is always a full PR review; prior findings become a regression checklist and the remediation delta is context only.

## Output contract

Return:

```text
merge_candidate_id
starting_revision
ending_revision
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
status: READY_FOR_FULL_REREVIEW | BLOCKED
next_action
```

`READY_FOR_FULL_REREVIEW` requires every known material review/check item to be resolved or explicitly blocked and reported.

## Handoff

- All known material findings/check failures reconciled → `pr-review` on the full current candidate.
- Authority/scope decision required → corresponding decision/work-item activity, then readiness before further production changes.
- Candidate missing/closed/merged → stop; do not create a replacement implementation path automatically.
- New unrelated work discovered → record a separate work item; do not expand this remediation candidate.
