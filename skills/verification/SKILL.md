---
name: verification
description: Establish revision-bound acceptance evidence for an issue or PR; not for repairing code or bypassing review and merge gates.
---

# Verification

## Invocation contract
Input: issue number or PR number, applicable acceptance criteria, exact candidate SHA when available.

## When to use
Use during `implement-issue` before gate 2 and during `pr-review` or `process-review` when checking a candidate's changed head.

## Do not use
Do not replace tests with confidence, silently change acceptance, or mark unrun checks passing.

## Required context
Read intended observable behavior, acceptance criteria, current code/PR revision, required checks and governing decisions. For PRs without an issue, derive explicit testable intent from PR and repository contracts.

## Stop or escalate when
Mandatory evidence is missing, criteria conflict with authority, tests fail, or head SHA changes during verification.

## Procedure
1. Freeze exact revision and criteria before inspecting results.
2. For each criterion, record command/fixture/measurement, actual result and PASS/FAIL/INCONCLUSIVE.
3. Check relevant negative, security, failure and integration behavior and all required checks. No skipped check silently passes.
4. Re-read head when revision sensitive. A changed head invalidates previous evidence.
5. Summarize blockers and precise next action. Never repair code during independent verification.

## Output contract
Return exact verified revision, criterion-to-evidence table, commands/results, missing evidence, verdict (VERIFIED | FAILED | INCONCLUSIVE) and next action.

## Handoff
VERIFIED → invoking skill; implementation defects → `implement-issue` before PR, `process-review` during PR review; missing authority → `create-issue`. VERIFIED does not waive `pr-review` or `pr-merge`.
