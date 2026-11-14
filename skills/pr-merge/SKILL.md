---
name: pr-merge
description: Merge a PR only after independent exact-head approval, required evidence, checks, rules and dependencies have been verified; not for review, remediation or admin bypass.
---

# PR merge

## Invocation contract
`/pr-merge <PR>` with exact PR number and caller merge authority. Invocation itself is the merge request; no redundant proceed prompt.

## When to use
Only after a completed independent `pr-review` has approved the current candidate and it is labeled `needs:merge` or equivalent.

## Do not use
Do not trust label alone, merge a stale approval, bypass protections, mark pending CI passed, force merge with unresolved blocking threads or provisional decisions, or close unrelated issues manually.

## Required context
Read `docs/WORKING-LOOP.md#task-first-execution-and-progressive-context`; consume existing evidence and fresh PR state/head/base, head-bound reviews (including self-review restrictions), required checks, branch protections/rulesets/code-owner requirements, unresolved blocking threads, linked issue/dependencies and merge method or queue.

## ADR merge authority

If applicable, follow `docs/WORKING-LOOP.md#adr-lifecycle-merge-is-acceptance`. This PR's final ADR can be accepted by authorized authoritative-branch merge; external unresolved prerequisites block. Verify actual merge commit and ADR content before reporting acceptance.

## Stop or escalate when
No independent current approval; changed diff/base invalidates evidence; any unresolved choice or external provisional contract prerequisite; missing checks, failures, conflicts, unmet review rules, dependencies, unverified mandatory criteria, unauthorized merge or head movement.

## Desktop-safe testing

Apply `docs/WORKING-LOOP.md#desktop-safe-test-execution` before any test or delegation: prefer non-disruptive or verified isolated execution; disruptive runs require explicit per-run human authorization when permitted. Never self-authorize. Unknown effects fail closed. Reuse only proven unaffected evidence; rerun required affected/exact-head checks. Unavailable mandatory evidence is NOT_RUN / INCONCLUSIVE; escalate, do not bypass.

## Procedure
1. Fetch candidate/head/base and freeze exact SHA; verify not already merged (idempotent status if so).
2. Confirm approved reviewer is independent of author and reviewed **this content**. Apply `docs/WORKING-LOOP.md#review-convergence-and-evidence-reuse`: require the final independent whole-candidate exact-head APPROVE, zero unresolved material blockers and no pending escalation; focused recheck or budget exhaustion never approves. A prior APPROVE plus newly added commits is not sufficient even if GitHub retains old review; re-review when necessary.
3. Validate required CI/check conclusions for head, current ruleset, code-owner/last-push approvals, thread requirements, dependency order, mergeability, that every required choice is resolved and every external ADR prerequisite is merged and verified (the PR's own final reviewed ADR is accepted at merge), and `Closes #N` issue mapping. Prefer a project's configured merge queue/strategy; do not invent a replacement strategy.
4. If all pass, merge the **same checked head** using authorized mechanism. Re-fetch to verify merge commit, target branch, exact ADR content where applicable, and linked issue closure. Report pending closure accurately. Release only owned transitional state/claims; do not erase historical evidence.
5. If head or base semantics changed before merge, stop and route to full re-review. Never claim success from a pending/failed merge action.

## Output contract
PR/approved head/merged head, compact reviewer/check/ruleset/thread/dependency result, merge strategy, confirmed commit URL and linked issue state, or BLOCKED with exact next action.

## Handoff
Merge verified → update milestone status; changed head or requirements → `pr-review`; review failures → `process-review`.
