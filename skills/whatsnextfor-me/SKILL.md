---
name: whatsnextfor-me
description: Select one unclaimed implementation-ready issue that best advances the active milestone; not for creating claims or starting implementation.
---

# What's next for me

## Invocation contract
`/whatsnextfor-me [milestone]`; optional current capacity or specialization may be supplied.

## When to use
Use when the user asks which issue to pick up next.

## Do not use
Do not select a claimed, blocked, unresolved-decision or duplicate issue; do not start work without explicit `implement-issue`.

## Required context
Use a fresh `describe-backlog` snapshot and any explicit priority, ownership, skill-match or milestone constraints.

## Stop or escalate when
No issue is verified READY, data is stale, or all available work is already claimed. Give the nearest unblocker rather than fabricate a task.

## Procedure
1. Invoke `describe-backlog`; consider only confirmed READY, unclaimed issues.
2. Rank by milestone dependency unlock, explicit priority, risk reduction and available capacity; do not optimize issue-count vanity metrics.
3. Return **one** recommendation plus up to two alternatives with evidence and blocking caveats.
4. Provide the exact command `/implement-issue <Issue>`; do not claim automatically.

## Output contract
Return recommended issue, evidence for readiness, why now, estimated complexity if grounded, alternatives and next command. If none READY, give one concrete unblocking action.

## Handoff
Selection → `implement-issue`. Missing DoR → `create-issue`.
