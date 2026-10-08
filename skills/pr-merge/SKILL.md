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
Do not trust label alone, merge a stale approval, bypass protections, mark pending CI passed, force merge with unresolved blocking threads, or close unrelated issues manually.

## Required context
Fresh PR state/head/base, head-bound reviews (including self-review restrictions), required checks, branch protections/rulesets/code-owner requirements, unresolved blocking threads, linked issue/dependencies and merge method or queue.

## Stop or escalate when
No independent current approval; changed diff/base invalidates evidence; missing checks, failures, conflicts, unmet review rules, dependencies, unverified mandatory criteria, unauthorized merge or head movement.

## Procedure
1. Fetch candidate/head/base and freeze exact SHA; verify not already merged (idempotent status if so).
2. Confirm approved reviewer is independent of author and reviewed **this content**. A prior APPROVE plus newly added commits is not sufficient even if GitHub retains old review; re-review when necessary.
3. Validate required CI/check conclusions for head, current ruleset, code-owner/last-push approvals, thread requirements, dependency order, mergeability and `Closes #N` issue mapping. Prefer a project's configured merge queue/strategy; do not invent a replacement strategy.
4. If all pass, merge the **same checked head** using authorized mechanism. Re-fetch to verify merge commit, target branch and linked issue closure. Report pending closure accurately. Release only owned transitional state/claims; do not erase historical evidence.
5. If head or base semantics changed before merge, stop and route to full re-review. Never claim success from a pending/failed merge action.

## Output contract
PR/approved head/merged head, reviewer/check/ruleset/thread/dependency matrix, merge strategy, confirmed commit URL and linked issue state, or BLOCKED with exact next action.

## Handoff
Merge verified → update milestone status; changed head or requirements → `pr-review`; review failures → `process-review`.
