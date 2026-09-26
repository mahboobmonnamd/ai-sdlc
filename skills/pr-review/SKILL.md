---
name: pr-review
description: Review one exact merge candidate for implementation correctness and merge readiness; not for editing/remediating the candidate, which belongs to address-pr-review.
---

# PR review

## Invocation contract

Required argument:

```text
merge_candidate_id: authoritative PR/MR/change-list identifier
```

Any request to review/re-review an existing merge candidate routes here. **There is no separate generic `code-review` skill.** If the user asks to fix review comments or failing required checks on a candidate already in review stage, use `address-pr-review`.

This skill remains independently usable (PRD UX-008): a caller may invoke it on a merge candidate without adopting the full AI-SDLC work-item lifecycle suite.

## When to use

Use whenever an existing merge candidate needs independent review. Every invocation, including re-review, covers the entire current candidate. Prefer candidates whose `candidate_lifecycle_stage` is `IN_REVIEW` (implementation complete enough that merge-readiness review is the intent). Do not use this as the primary route for unfinished feature implementation.

## Do not use

- Do not infer readiness from green CI, resolved threads, reviewer confidence, or plausible code.
- Do not limit re-review to the latest delta or old findings.
- Do not stop at the first blocker or an arbitrary finding count.
- Do not remediate code in a review-only pass.
- Do not treat a missing plan as an automatic review failure when lifecycle plan context is `NOT_APPLICABLE`.

## Lifecycle context (conditional)

Resolve optional lifecycle bindings with explicit states. Use these labels:

```text
lifecycle_work_item: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
lifecycle_accepted_plan: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
```

Rules:

1. When the candidate is owned by an AI-SDLC work-item workflow, or project/rigor policy requires a plan for this change class, treat the accepted plan as required.
2. When no owning work item / accepted plan applies (external contributor PR, dependency bump, docs/config-only change, legacy PR, or project policy that does not require a plan), set the corresponding state to `NOT_APPLICABLE` and continue.
3. `AVAILABLE` means the binding exists and is resolvable (for plans: exact accepted `plan_id + plan_revision` with acceptance evidence, current governing revisions).
4. `REQUIRED_BUT_MISSING` means policy/workflow requires the binding but it cannot be resolved → return `INCONCLUSIVE` or `BLOCKED_BY_DECISION` (prefer `INCONCLUSIVE` when access/resolution failed; `BLOCKED_BY_DECISION` when an authority/policy decision is needed to proceed). Do not invent a plan.
5. `NOT_APPLICABLE` must not make the review inconclusive. Review against candidate intent, repository authority, tests/checks, and applicable requirements instead.

Privacy gating for external indexes and exact-revision verification remain mandatory regardless of lifecycle context.

## Required context

Always load: candidate identity/base/current revision, actual diff plus materially affected production paths, tests/checks/CI, applicable measurements/specialist evidence, documentation/PR claims, and prior findings on re-review.

Conditionally load when `AVAILABLE`: owning work item, accepted implementation plan `plan_id` + `plan_revision` + governing revisions + acceptance evidence, acceptance/Done rules, and governing authority from that lifecycle. When `NOT_APPLICABLE`, reconstruct intent from the candidate description, repository norms, and any linked tracker/issue text that is present without requiring the full suite.

## Stop or escalate when

Block or return inconclusive for authority/scope conflicts, weakened evidence, stale revision evidence, unclassified temporary/duplicate production paths, missing required specialist evidence, environment-limited mandatory evidence without an authorized substitute, or insufficient access to trace the real production path.

For lifecycle bindings: only `REQUIRED_BUT_MISSING` plan/work-item context blocks or returns inconclusive for that reason. A `NOT_APPLICABLE` missing plan does not.

A changed candidate revision invalidates the prior merge-readiness verdict.

## Procedure

1. Freeze candidate identity: base, exact revision, state/mergeability, changed surfaces, and `candidate_lifecycle_stage` when known (`IMPLEMENTATION_IN_PROGRESS` | `IN_REVIEW`). If the stage is still `IMPLEMENTATION_IN_PROGRESS`, do not treat this as merge-readiness review; route back to `implementation` (or report that full PR review is premature).
2. Classify lifecycle context (`AVAILABLE` / `NOT_APPLICABLE` / `REQUIRED_BUT_MISSING`) for work item and accepted plan. When `AVAILABLE`, reconstruct work-item outcome, resolve the accepted-plan reference, then load immutable content for that exact `plan_id + plan_revision`; if that exact revision is not resolvable under a required binding, return inconclusive/blocked rather than falling back to latest. Verify governing revisions are still current. Do not choose an arbitrary related/latest plan. When `NOT_APPLICABLE`, reconstruct candidate intent and applicable repository/requirement authority without a plan. When `REQUIRED_BUT_MISSING`, stop with the inconclusive/blocked outcome above.
3. Build full review coverage: changed files, affected surrounding paths, ownership/API/data/trust boundaries, failure/lifecycle/concurrency paths, checks/evidence, and material risk domains.
4. Review implementation correctness and permanent-production intent across that full map.
5. Verify architecture/authority was not silently changed.
6. Audit tests and required checks for weakened assertions, skipped/bypassed paths, mocks/fakes that replace production behavior, stale artifacts, and revision mismatch.
7. Run or consume `verification`; for revision-sensitive evidence require `verified_revision == reviewed_revision` unless project policy explicitly authorizes carry-forward. Reconsider every mandatory criterion as `PROVEN | FAILED | INCONCLUSIVE | ENVIRONMENT_UNSUPPORTED`.
8. Audit material measurements by actual boundary, workload, environment/configuration, statistics, instrumentation, and exact revision.
9. Run/consume only specialist reviews required by project policy or material risk.
10. Compare PR/docs/work-item (when available) claims with the exact implementation and evidence.
11. Adversarially inspect important unrepresented failure/race/recovery/lifecycle states.
12. Continue after blockers and report **all material blockers discovered in this pass**; group duplicate symptoms by root cause without hiding independent defects.
13. On re-review, verify every prior finding, then run the **entire procedure again over the entire current candidate**. Prior findings are a regression checklist; the remediation delta is context only.
14. Re-resolve the exact revision before verdict. If it changed, restart the full review.
15. Synthesize one verdict; a single unresolved mandatory blocker prevents readiness.

## Output contract

```text
verdict: READY_TO_MERGE | CONDITIONAL | CHANGES_REQUIRED | BLOCKED_BY_DECISION | INCONCLUSIVE
merge_candidate_id
reviewed_revision
base_revision_or_target
candidate_lifecycle_stage: IMPLEMENTATION_IN_PROGRESS | IN_REVIEW | UNKNOWN
lifecycle_work_item: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
lifecycle_accepted_plan: AVAILABLE | NOT_APPLICABLE | REQUIRED_BUT_MISSING
verification_evidence_revision: <exact revision> | NOT_REVISION_SENSITIVE | INCONCLUSIVE
blocking_findings
review_coverage
prior_finding_disposition
non_blocking_findings
acceptance_matrix
evidence_matrix
measurement_table_if_applicable
residual_risks
merge_recommendation: YES | NO | ONLY_AFTER_LISTED_CONDITIONS
```

`READY_TO_MERGE` requires no blocking finding and sufficient exact-revision evidence for every mandatory criterion. Environment limitation alone is never a pass.

## Handoff

- Ready → merge/release authority; this skill does not merge by default.
- Implementation/test/measurement defect on an `IN_REVIEW` candidate → `address-pr-review`, then full `pr-review`.
- Candidate still `IMPLEMENTATION_IN_PROGRESS` → `implementation` (not merge-readiness remediation).
- Missing acceptance evidence when plan context is `AVAILABLE` or required → `verification`/applicable specialist activity, then full `pr-review`.
- Scope/authority conflict → design/decision workflow + `development-readiness` when an owning work item exists.
- Revision changed → full-review the new candidate.

There is no hard review-round cap. Convergence target: one complete finding pass + one full re-review after batched remediation when feasible.
