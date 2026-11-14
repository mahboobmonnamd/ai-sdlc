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
Read `docs/WORKING-LOOP.md#task-first-execution-and-progressive-context`; consume the existing evidence packet, intended behavior, current revision and applicable checks/authority. Load only affected sources; update the same packet. For PRs without an issue, derive explicit testable intent from PR and repository contracts.

## Stop or escalate when
Mandatory evidence is missing, criteria conflict with authority, tests fail, or head SHA changes during verification.

## Desktop-safe testing

Apply `docs/WORKING-LOOP.md#desktop-safe-test-execution` before any test or delegation: prefer non-disruptive or verified isolated execution; disruptive runs require explicit per-run human authorization when permitted. Never self-authorize. Unknown effects fail closed. Reuse only proven unaffected evidence; rerun required affected/exact-head checks. Unavailable mandatory evidence is NOT_RUN / INCONCLUSIVE; escalate, do not bypass.

## Procedure
1. Freeze exact revision and criteria before inspecting results.
2. For each criterion, record command/fixture/measurement, actual result and PASS/FAIL/INCONCLUSIVE.
3. Check relevant negative, security, failure and integration behavior and all required checks. No skipped check silently passes.
4. Re-read head when revision sensitive. A changed head requires reassessment under `docs/WORKING-LOOP.md#review-convergence-and-evidence-reuse`. Invalidate affected or unknown-provenance evidence; rerun all mandatory exact-head checks. Link unchanged historical results only with verified equivalence of relevant code, transitive dependencies, contracts, fixtures, tools and config; never claim they were run at new SHA. Record reuse rationale and invalidated items.
5. Summarize blockers and precise next action. Never repair code during independent verification.

## Output contract
Return exact verified revision, criterion-to-evidence table, commands/results, missing evidence, verdict (VERIFIED | FAILED | INCONCLUSIVE) and next action.

## Handoff
VERIFIED → invoking skill; implementation defects → `implement-issue` before PR, `process-review` during PR review; missing authority → `create-issue`. VERIFIED does not waive `pr-review` or `pr-merge`.
