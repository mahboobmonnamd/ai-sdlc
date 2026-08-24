---
name: verification
description: Prove whether the requested outcome and acceptance criteria are actually satisfied using traceable evidence, independently from implementation and code-review confidence.
---

# Verification

## When to use

Use after implementation and applicable review are complete, or whenever someone asks whether a feature/change is actually done, accepted, or proven against its intended outcome.

## Do not use

- Do not equate compilation, passing unit tests, merged code, or reviewer approval with outcome verification.
- Do not change acceptance criteria after seeing the implementation unless the owning authority explicitly revises them.
- Do not invent missing evidence, measurements, or user behavior.
- Do not repair implementation silently while acting as an independent verifier; return failures to the appropriate activity.
- Do not assume one verification technique fits every project or risk profile.

## Required context

Load:

- original intended outcome and accepted requirements;
- work-item acceptance criteria and non-goals;
- governing specifications/decisions;
- implementation/review evidence and known limitations;
- required test, integration, demo, measurement, security, accessibility, operational, or documentation evidence;
- applicable rigor profile.

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

1. Translate every applicable acceptance criterion into one or more evidence items before considering the implementation result.
2. Map each evidence item to its authoritative source so success cannot be redefined opportunistically.
3. Gather or execute the strongest practical evidence appropriate to the risk profile: tests, integration behavior, fixtures, reproducible demos, measurements, failure injection, specialist reviews, documentation checks, or operational checks.
4. Verify negative behavior and important failure conditions where they are part of the contract, not only the successful path.
5. Compare measured values with explicit targets/budgets when performance, reliability, capacity, or resource constraints are acceptance requirements.
6. Check that deferred/non-goal behavior remains accurately classified and has not been falsely claimed complete.
7. Confirm the production path contains only permanent-intent implementation for the accepted scope. An MVP may be narrow, but verification must fail if completion depends on disposable POC code or a competing temporary implementation.
8. Distinguish implementation defects from missing/invalid acceptance criteria or authority decisions.
9. Record PASS/FAIL/INCONCLUSIVE per criterion with evidence references. An absent evidence item is not a pass.
10. Produce a final verdict only from the criterion-level evidence, not from overall confidence.
11. Preserve the evidence needed for a later human/agent to reproduce or audit the verdict.

## Output contract

Return:

```text
verdict: VERIFIED | FAILED | INCONCLUSIVE | BLOCKED_BY_DECISION
criteria:
  - criterion
    result: PASS | FAIL | INCONCLUSIVE
    evidence
    source_authority
failures_or_gaps
measurements_and_targets (when applicable)
known_deferred_or_non_goal_behavior
next_action
```

`VERIFIED` requires every mandatory acceptance criterion to have sufficient passing evidence.

## Handoff

- VERIFIED → `release-readiness` or project completion workflow.
- Implementation defect → `implementation`, then `code-review`/`verification` as appropriate.
- Acceptance/authority defect → upstream requirements/decision skill, then `development-readiness`.
- Missing evidence → obtain the required test/measurement/specialist evidence and re-run verification.
