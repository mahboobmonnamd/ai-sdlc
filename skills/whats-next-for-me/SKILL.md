---
name: whats-next-for-me
description: Recommend one unclaimed, actually ready GitHub issue that most helps the current milestone; not for claiming or implementing the item.
---

# What's next for me

## Invocation contract
`/whats-next-for-me [milestone]`; optional specialization/capacity constraints.

## When to use
User wants the single next issue to implement rather than a large backlog report.

## Do not use
Do not choose a claimed, dependency-blocked, duplicate, unresolved-design or merely labeled-ready ticket. No automatic implementation.

## Required context
Use current `describe-backlog` evidence and explicitly declared priorities, dependencies and developer capacity, where known.

## Stop or escalate when
No candidate is confirmed ready or inventory incomplete for a confident ranking. Present the highest-value unblocker instead of guessing.

## Procedure
1. Filter to independent, DoR-passing `needs:implementation` issues with no active owner/PR and satisfied dependencies.
2. Prefer milestone-critical dependency unlock and explicit priority; then reduced implementation/review risk and suitable scope. Never optimize raw number of closed tickets.
3. Recommend **one** issue with a concrete why-now explanation, source and `/implement-issue <N>`; optionally show two alternatives.
4. Do not claim or edit the issue. Claim eligibility must be revalidated when `implement-issue` starts.

## Output contract
One recommendation or no-ready verdict, evidence for DoR/claim/dependencies, risks/alternatives and exact next command.

## Handoff
Recommended → `implement-issue`; if none → `create-issue` for the top unblocker.
