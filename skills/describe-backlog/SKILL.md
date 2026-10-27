---
name: describe-backlog
description: Retrieve and verify ready, active, blocked and refinement work for a milestone or project; not for claiming issues or fabricating priority.
---

# Describe backlog

## Invocation contract
`/describe-backlog [milestone]`; optional risk, workstream or priority filter.

## When to use
When planning available implementation work or explaining why work is blocked.

## Do not use
Do not infer ready from a label alone, promote duplicate/in-flight work, count parent and child as independent delivery twice, or mutate issues.

## Required context
Fresh paginated issues/PRs, milestones, exact DoR, implementation and review claims, accepted dependencies, plans and explicit priority.

## Stop or escalate when
Pagination/permissions, claimant or dependency state is unavailable; mark counts as PARTIAL/UNKNOWN and name missing data.

## Procedure
1. Fetch all matching pages with snapshot timestamp. Join each issue to related PRs (including closed-unmerged/merged), owner/claim, scope and dependency state.
2. Reconcile DoR for potential READY items and identify material `!+concern` blocks. An issue can be ready without an optional verification command but not without measurable evidence.
3. Categorize mutually exclusively: READY, IMPLEMENTING, REVIEW, PROCESSING, MERGE_READY, BLOCKED, NEEDS_REFINEMENT, DONE or UNKNOWN. Avoid double counting parent/child outcomes.
4. Sort READY by actual milestone priority and dependency unlock, then risk reduction; note ties and missing estimates rather than invent scores.
5. Show concise ready list plus blockers/unblock actions, status totals, source links and data completeness. Never claim/assign issues from this command.

## Output contract
Milestone, snapshot freshness/completeness, ready table (number, outcome, why now, dependencies, ownership), blocked and in-flight evidence, counts, gaps and next command.

## Handoff
Use `whats-next-for-me` for one recommendation, `implement-issue <N>` to claim after Gate 1, `create-issue` for non-ready refinement.
