---
name: pr-merge
description: Verify an approved exact PR head and repository branch protections before merging it; not for approving, remediating, or overriding safeguards.
---

# PR merge

## Invocation contract
`/pr-merge <PR>` requires PR number and merge authority.

## When to use
Use after an independent approving `pr-review` for the current head.

## Do not use
Do not merge a stale or unapproved head, bypass checks/reviews/protection, assume queued checks are passing, or merge a blocked dependency early.

## Required context
Current PR head/base/mergeability, latest non-dismissed reviews, outstanding requested changes, required checks, branch protection, active review threads, linked issue/dependencies and authorized merge method.

## Stop or escalate when
Approval does not match exact head, PR changed since review, required checks failed/pending, merge conflicts exist, review blockers/locks remain, or caller lacks permission.

## Procedure
1. Re-fetch and record exact head/base. Verify `needs:merge` is only a hint; a valid APPROVE review for **this head** is mandatory.
2. Verify required checks, branch protections, unresolved blocking threads, acceptance evidence, dependencies and mergeability. Do not use admin bypass.
3. Choose project-approved merge strategy (squash/rebase/merge); use protected merge queue when mandated.
4. Merge the verified head once, not an approximate/stale candidate. Recheck result and actual merge commit on the target.
5. Let `Closes #N` close the linked issue when merged into default branch; verify closure instead of closing unrelated tickets. Clean transitional labels and release owned claims. Report exceptions instead of claiming success.

## Output contract
Return: PR/head reviewed/head merged, approval/CI/threads/protection status, merge method, merge commit and URL, linked issue closure, or BLOCKED with reasons.

## Handoff
Successful merge → project completion/release tracking. Any head change → `pr-review`; review failures → `process-review`.
