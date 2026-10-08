---
name: process-review
description: Reconcile and fix all material review findings and required-CI failures on the same PR in one approved batch; not for unfinished feature implementation or final approval.
---

# Process review

## Invocation contract
`/process-review <PR>` with exact PR number; continue existing candidate only.

## When to use
Review-stage PR with requested changes, unresolved material threads or failed required checks.

## Do not use
Do not fix only the latest comment, blindly obey suggestions, create a second PR, silently expand feature scope, change valid tests to pass, self-approve, or close unresolved concerns to appear green.

## Required context
Current head/base, ownership and stage, **all** review threads/comments and prior blocking findings, all required checks/logs, issue/AC or reconstructed standalone intent, authority, affected code and tests.

## Stop or escalate when
Candidate already merged/rejected or incomplete feature scope should route to `implement-issue`; conflicting owner/claim; head changed after preview; proposal requires new product/security/architecture decision or unrelated scope.

## Procedure
1. Confirm PR is `IN_REVIEW`/reopenable `CLOSED_UNMERGED`, not unfinished implementation. Atomically claim shared `pr:<N>` exclusion and confirm owner/token; transition `needs:processing` → `pr:processing`. Re-fetch exact head.
2. Collect every unresolved thread, blocking past finding and failing required check; check against **current code**. Group duplicate symptoms by root cause without omitting independently material defects.
3. Assign each exactly one disposition and proof:
   - **should fix** — valid in-scope defect, regression or required missing evidence;
   - **improvement** — non-blocking; make optional, normally defer unless user elects to include;
   - **discard** — duplicate, obsolete or factually wrong, with source proof;
   - **disagree** — evidence-based non-blocking difference; reply and leave review authority to reassess;
   - **push back** — an unresolved reviewer/owner decision; don't silently choose.
4. **Single gate:** show one complete decision table: finding/thread/CI link, proposed disposition, root cause, planned files and fix, tests, optional changes, open authority blockers and exact head. Ask **"Apply this plan? (yes/no)"**. On no, perform no code/reply/thread mutations and release claim conditionally. Do not seek approval for each comment.
5. On yes, recheck head, claim and governing authority; fix accepted `should fix` root causes **and sibling instances** on the existing branch. Include approved improvements only when in scope and not delaying mandatory closure. Run targeted + risk/required checks; never weaken existing criteria. If an authority blocker remains, safely fix independent approved items then report what waits.
6. Push only approved and verified remediation to same PR; record old/new SHA and exact evidence. Reply once per relevant thread with rationale and test proof; resolve threads only where materially addressed and project permissions allow. `disagree`/`push back` are not self-closed as "fixed."
7. Re-inventory full current review/CI state and each ledger row: FIXED, SUPERSEDED_WITH_PROOF, BLOCKED, or DEFERRED_NONBLOCKING. When mandatory blockers are fixed and review authority can reassess outstanding disagreements, transition `pr:processing` → `needs:review`, release claim, and route to **full** `pr-review` of exact new head. Otherwise report BLOCKED, preserve same candidate and safely release/retain per project policy.

## Output contract
PR/current revision; complete disposition + root-cause ledger; single approval response; before/after head; files/tests/CI evidence; comment/reply/thread actions; remaining blockers; label stage and next action.

## Handoff
Resolved batch → `pr-review`; incomplete accepted feature work → `implement-issue`; unresolved decision → named authority and keep same PR; follow-up IMPR → separate issue only with project authorization.
