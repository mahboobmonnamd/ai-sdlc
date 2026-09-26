---
name: verification
description: Prove acceptance outcomes with revision-traceable evidence; not for fixing implementation defects or bypassing a PR-review gate required by project policy.
---

# Verification

## Invocation contract

Required input is one verification target, plus revision when the evidence is revision-sensitive:

```text
verification_target: work_item | merge_candidate
work_item_id: required when verification_target is work_item
merge_candidate_id: required when verification_target is merge_candidate
candidate_intent: required when verification_target is merge_candidate; reconstructed from the candidate description, repository authority, and applicable requirements
candidate_revision: exact implementation revision when verification is revision-sensitive
```

Use `work_item` when an owning work item is available. Use `merge_candidate` when `pr-review` classified `lifecycle_work_item` as `NOT_APPLICABLE` (external, docs, dependency, legacy, or other no-work-item candidates). Do not invent a work item to satisfy this skill. Do not require `work_item_id` for that target.

A consuming project may omit `candidate_revision` only when its evidence model is explicitly not revision-sensitive. Never guess a revision when the host exposes one. When a revision is supplied, verification must return that exact verified revision.

## When to use

Use after implementation when acceptance evidence must be proven, when invoked as the evidence stage inside `pr-review`, or whenever someone asks whether a feature/change is actually done, accepted, or proven against its intended outcome. Verification does not require a prior PR-review verdict, but a standalone VERIFIED result does not waive any PR-review gate required by project or rigor policy.

## Do not use

- Do not equate compilation, passing unit tests, merged code, or reviewer approval with outcome verification.
- Do not change acceptance criteria after seeing the implementation unless the owning authority explicitly revises them.
- Do not invent missing evidence, measurements, or user behavior. If a source cannot be established, write `unknown`.
- Do not repair implementation silently while acting as an independent verifier; return failures to the appropriate activity.
- Do not add an opportunistic test suite while verifying; missing required evidence is FAIL or INCONCLUSIVE.
- Do not assume one verification technique fits every project or risk profile.

## Required context

Load:

- original intended outcome;
- when `verification_target` is `work_item`: work-item acceptance criteria and non-goals;
- when `verification_target` is `merge_candidate`: candidate intent, repository authority, tests/checks, and applicable requirements — do not require a work item;
- governing specifications/decisions when they apply;
- implementation/review evidence and known limitations;
- required test, integration, demo, measurement, security, accessibility, operational, or documentation evidence;
- applicable rigor profile;
- `candidate_lifecycle_stage` when a merge candidate exists.

## Stop or escalate when

Verification cannot pass when:

- acceptance criteria are ambiguous, contradictory, stale, or not objectively testable;
- authoritative behavior changed without approved updates;
- required evidence is unavailable, non-reproducible, or based only on agent assertion;
- a mandatory specialist review/gate has not completed;
- implementation scope differs materially from the accepted outcome;
- exploratory/spike/prototype/POC code or a temporary parallel implementation remains on the production path without formal production reclassification and normal quality gates;
- a failure reveals a product/architecture decision rather than an implementation defect.

## Procedure

1. Resolve and record `candidate_revision` before gathering revision-sensitive evidence. If no revision applies under project policy, record `NOT_REVISION_SENSITIVE`.
2. Translate every applicable acceptance criterion into one or more evidence items before considering the implementation result. For `verification_target: work_item`, criteria come from the work item. For `verification_target: merge_candidate`, criteria come from candidate intent, repository authority, tests/checks, and applicable requirements.
3. Map each evidence item to its authoritative source so success cannot be redefined opportunistically.
4. Gather or execute the strongest practical evidence appropriate to the risk profile: tests, integration behavior, fixtures, reproducible demos, measurements, failure injection, specialist reviews, documentation checks, or operational checks.
5. Verify negative behavior and important failure conditions where they are part of the contract, not only the successful path.
6. Compare measured values with explicit targets/budgets when performance, reliability, capacity, or resource constraints are acceptance requirements.
7. Check that deferred/non-goal behavior remains accurately classified and has not been falsely claimed complete.
8. Confirm the production path contains only permanent-intent implementation for the accepted scope. An MVP may be narrow, but verification must fail if completion depends on disposable POC code or a competing temporary implementation.
9. Distinguish implementation defects from missing/invalid acceptance criteria or authority decisions.
10. Record PASS/FAIL/INCONCLUSIVE per criterion with evidence references. Quote the exact command, test, output line, or measurement. An absent evidence item is not a pass. Agent assertion is not evidence.
11. Produce a final verdict only from the criterion-level evidence, not from overall confidence. For a work item, Done is that item’s 3–5 checkable conditions. For a merge candidate with no work item, Done is the candidate-intent criteria. Never “production-ready” or “looks good.”
12. Preserve the evidence needed for a later human/agent to reproduce or audit the verdict.
13. Re-resolve the candidate revision before final verdict when the host exposes one. If it changed, revision-sensitive evidence is stale and the result cannot be VERIFIED until evidence is gathered for the new revision.

## Output contract

Every result includes `effects`: the list of effect ids for actions this invocation performed. Omitting `effects` is not an empty trace.

Return:

```text
verdict: VERIFIED | FAILED | INCONCLUSIVE | BLOCKED_BY_DECISION
verification_target: work_item | merge_candidate
verified_revision: <exact revision> | NOT_REVISION_SENSITIVE
revision_sensitivity: REVISION_SENSITIVE | NOT_REVISION_SENSITIVE
evidence_revision_evaluated: <revision evidence was gathered for> | NOT_REVISION_SENSITIVE
head_revision: <current candidate head when known> | UNKNOWN
criteria_evidence: PRESENT | MISSING
next_action: pr-review | implementation | address-pr-review | release-readiness | obtain-evidence | decision-activity
criteria:
  - criterion
    result: PASS | FAIL | INCONCLUSIVE
    evidence: quoted command/output/source or `unknown`
    source_authority
failures_or_gaps
measurements_and_targets (when applicable)
known_deferred_or_non_goal_behavior
next_action
```

`VERIFIED` requires every mandatory acceptance criterion to have sufficient passing evidence and, when revision-sensitive, `verified_revision` to equal the revision actually evaluated.

## Handoff

- VERIFIED when invoked by `pr-review` → return criterion-level evidence to that `pr-review`.
- Standalone VERIFIED with an existing merge candidate or a project/rigor policy that requires PR review → `pr-review`; do not route directly to release readiness.
- Standalone VERIFIED only when no PR-review gate applies → `release-readiness` or project completion workflow.
- Implementation defect on an open merge candidate:
  - `IN_REVIEW` → `address-pr-review`, then full `pr-review`;
  - `IMPLEMENTATION_IN_PROGRESS` → `implementation`;
  - `UNKNOWN` → stop and reconcile the durable stage; do not guess;
  - no merge candidate yet → `implementation`.
- Acceptance/authority defect → upstream requirements/decision skill, then `development-readiness`.
- Missing evidence → obtain the required test/measurement/specialist evidence and re-run verification.
