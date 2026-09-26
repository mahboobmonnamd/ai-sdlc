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

Any request to review/re-review an existing merge candidate routes here. **There is no separate generic `code-review` skill.** If the user asks to fix review comments or failing required checks, use `address-pr-review`.

## When to use

Use whenever an existing merge candidate needs independent review. Every invocation, including re-review, covers the entire current candidate.

## Do not use

- Do not infer readiness from green CI, resolved threads, reviewer confidence, or plausible code.
- Do not limit re-review to the latest delta or old findings.
- Do not stop at the first blocker or an arbitrary finding count.
- Do not remediate code in a review-only pass.

## Required context

Load the candidate identity/base/current revision, owning work item, accepted implementation plan `plan_id` + `plan_revision` + governing revisions, acceptance/Done rules, governing authority, actual diff plus materially affected production paths, tests/checks/CI, applicable measurements/specialist evidence, documentation/PR claims, and prior findings on re-review.

## Stop or escalate when

Block or return inconclusive for authority/scope conflicts, stale/missing plan or acceptance, weakened evidence, stale revision evidence, unclassified temporary/duplicate production paths, missing required specialist evidence, environment-limited mandatory evidence without an authorized substitute, or insufficient access to trace the real production path.

A changed candidate revision invalidates the prior merge-readiness verdict.

## Procedure

1. Freeze candidate identity: base, exact revision, state/mergeability, changed surfaces.
2. Reconstruct work-item outcome, resolve the work item's/project registry's accepted-plan reference, then load immutable content for that exact `plan_id + plan_revision`; if that exact revision is not resolvable, block/inconclusive rather than falling back to latest. Verify its governing revisions are still current. Do not choose an arbitrary related/latest plan. Then reconstruct architecture/scope constraints, acceptance criteria, and required evidence.
3. Build full review coverage: changed files, affected surrounding paths, ownership/API/data/trust boundaries, failure/lifecycle/concurrency paths, checks/evidence, and material risk domains.
4. Review implementation correctness and permanent-production intent across that full map.
5. Verify architecture/authority was not silently changed.
6. Audit tests and required checks for weakened assertions, skipped/bypassed paths, mocks/fakes that replace production behavior, stale artifacts, and revision mismatch.
7. Run or consume `verification`; for revision-sensitive evidence require `verified_revision == reviewed_revision` unless project policy explicitly authorizes carry-forward. Reconsider every mandatory criterion as `PROVEN | FAILED | INCONCLUSIVE | ENVIRONMENT_UNSUPPORTED`.
8. Audit material measurements by actual boundary, workload, environment/configuration, statistics, instrumentation, and exact revision.
9. Run/consume only specialist reviews required by project policy or material risk.
10. Compare PR/docs/work-item claims with the exact implementation and evidence.
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
- Implementation/test/measurement defect → `address-pr-review`, then full `pr-review`.
- Missing acceptance evidence → `verification`/applicable specialist activity, then full `pr-review`.
- Scope/authority conflict → design/decision workflow + `development-readiness`.
- Revision changed → full-review the new candidate.

There is no hard review-round cap. Convergence target: one complete finding pass + one full re-review after batched remediation when feasible.
