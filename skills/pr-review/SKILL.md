---
name: pr-review
description: Independently examine the entire current PR diff and post a structured GitHub review with inline findings; not for changing code or merging.
---

# PR review

## Invocation contract
`/pr-review <PR>` requires a concrete PR number.

## When to use
Use for an initial review or full re-review of an open candidate, including candidates with no AI-SDLC issue.

## Do not use
Do not edit PR code, approve unverified blockers, review only the latest delta, or mistake green CI for correctness.

## Required context
Fetch current PR head/base, changed files and full diff, issue intent if available, authority/design decisions, check runs, threads and prior reviews. Resolve current main/base before analysis.

## Stop or escalate when
PR is merged/closed, another reviewer owns its claim, the diff cannot be fully inspected, the base/head becomes stale, or mandatory evidence is unavailable. Report INCONCLUSIVE rather than pretend APPROVED.

## Procedure
1. Check whether changes are already merged/equivalent, PR is stale against base, base branch is missing, or head changed since prior review. Report and stop when substantive review is inapplicable.
2. Atomically claim review ownership; confirm it, then transition `needs:review` → `pr:reviewing`. A second simultaneous claimant loses; labels are never sufficient for exclusion.
3. Freeze exact head SHA and base. Inspect **all changed files plus affected call paths**, contracts, security boundaries, data migrations, concurrency/failure paths and tests. For re-review, check previous findings and review the complete candidate again.
4. Classify material findings `[CRIT]` correctness/reliability, `[SEC]` security/privacy, `[NONCONF]` intent/spec violation, `[IMPR]` non-blocking quality improvement, `[GOOD]` meaningful strengths. Combine duplicates by root cause.
5. Give actionable inline comments on exact changed lines for defects; include expected behavior, failure case and suggested evidence. Never post fabricated inline positions. Include a concise summary and acceptance/CI coverage table in the **structured GitHub review**.
6. Recheck head before submission. **REQUEST_CHANGES** for any unresolved CRIT/SEC/NONCONF or mandatory evidence gap; **APPROVE** when no blocking issues remain (IMPR-only may approve). If GitHub forbids own-PR approval, return a non-approval review with the same findings and state the constraint. Inconclusive reviews are not approvals.
7. Submit exactly one coherent review for this head, then set `needs:processing` on changes requested, or `needs:merge` on approved exact head; remove `pr:reviewing`, and release the claim. Never advance a changed head using stale approval.

## Output contract
Return: PR/head/base, stale/duplicate assessment, classification counts, inline comment links when posted, criterion/CI coverage, decision (APPROVE | REQUEST_CHANGES | INCONCLUSIVE), review URL, label outcome and next action.

## Handoff
REQUEST_CHANGES → `process-review`. APPROVE → `pr-merge`. A new head must be fully re-reviewed.
