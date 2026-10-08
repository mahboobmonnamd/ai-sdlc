---
name: describe-backlog
description: Produce an evidence-based shortlist of actionable ready issues from the project backlog; not for assigning, claiming or implementing them.
---

# Describe backlog

## Invocation contract
`/describe-backlog [milestone]` optionally scopes a current GitHub milestone.

## When to use
Use to understand ready work, dependencies, blocked work and available parallel tasks.

## Do not use
Do not assume any open issue is ready, duplicate active work, infer priority from issue number, or silently assign owners.

## Required context
Fetch current issues/labels/milestones, existing active claims, dependencies, Definition of Ready and related PRs. Respect pagination.

## Stop or escalate when
The issue list or dependency state is incomplete; clearly mark a partial snapshot rather than inventing completeness.

## Procedure
1. Exclude closed/merged/claimed/duplicate issues and blocked dependencies.
2. Check all required DoR fields for remaining `needs:implementation` candidates; optional verification command may be absent.
3. Group as READY, BLOCKED, IN_PROGRESS, or NEEDS_REFINEMENT and give a precise blocking reason.
4. Rank READY issues by explicit milestone priority, dependency unlock and risk; label ties instead of inventing priority.

## Output contract
Return snapshot date, scope/milestone, totals by status, concise ready issue table (number/title/priority/dependencies/why-next), blocked reasons and evidence links. No GitHub writes.

## Handoff
`whatsnextfor-me` selects one from this evidence; `implement-issue <Issue>` claims it.
