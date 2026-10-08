---
name: process-review
description: Triage all current review feedback and required-check failures, get one approval, then remediate the same PR; not for new feature scope or final approval.
---

# Process review

## Invocation contract
`/process-review <PR>` requires PR number.

## When to use
Use for PRs labeled `needs:processing` after a blocking review or for existing review feedback needing disposition.

## Do not use
Do not blindly obey reviewer comments, address only the newest comment, rewrite acceptance, start a new PR, or push before the single gate.

## Required context
Current PR head/base, complete review threads and prior finding history, failing required checks, issue intent, affected code/tests, and update authority.

## Stop or escalate when
PR is already merged, another processor holds the claim, branch/head moves unexpectedly, work exceeds accepted scope, or an unresolved product/security authority decision is needed.

## Procedure
1. Atomically claim PR processing; confirm it, then transition `needs:processing` → `pr:processing`. If not acquired, stop before changing files/labels.
2. Refresh PR head and inventory **all** comments, unresolved threads, review blockers and required CI failures; verify each against current code (not just old comments).
3. Group by root cause. Give every item exactly one disposition:
   - **should fix** — valid in-scope defect or missing mandatory evidence;
   - **improvement** — optional polish, keep separate unless expressly approved;
   - **discard** — duplicate/obsolete/incorrect with proof;
   - **disagree** — non-blocking counterargument with evidence;
   - **push back** — decision/clarification needed from reviewer or authority.
4. **Single gate**: show full decision table (source/thread, category, disposition, reasoning, planned action, tests, owner/blocker), current head and exact files expected to change. Ask **"Apply this plan? (yes/no)"**. No edits, pushes, thread resolutions or replies before yes. On no, preserve findings and release ownership safely.
5. On yes, recheck head/claim and apply only approved changes on **the same PR branch**. Fix root causes, run affected tests and all mandatory checks. Never close a thread just to make the dashboard green.
6. Post concise evidence-based replies and resolve only addressed threads when allowed. Keep `push back` and unproven required findings open. Mark each table row FIXED / DEFERRED / REJECTED_WITH_REASON / BLOCKED.
7. If all material blockers resolved and evidence current, transition `pr:processing` → `needs:review`, release claim and request full `pr-review` of new head. Otherwise remain blocked with a precise next action; release or retain claim according to explicit recovery policy.

## Output contract
Return: head before/after, complete decision table, approval response, changed files, tests/evidence, posted replies/resolved threads, remaining blockers and next stage.

## Handoff
All mandatory findings resolved → `pr-review`. Missing authority → named decision owner. Optional improvements may become separate issues.
