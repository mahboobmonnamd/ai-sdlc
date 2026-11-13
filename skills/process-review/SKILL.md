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

For ADR-related findings, follow `docs/WORKING-LOOP.md#adr-lifecycle-merge-is-acceptance`: revise the ADR in the same authorized decision PR and obtain exact-head re-review. Do not create a second PR merely to change Proposed to Accepted. A separate dependent implementation must reconcile the actual external ADR merge before its final review; do not close a genuinely unresolved choice as a status-only issue.

## Stop or escalate when
Candidate already merged/rejected or incomplete feature scope should route to `implement-issue`; conflicting owner/claim; head changed after preview; proposal requires new product/security/architecture decision or unrelated scope.

## Desktop-safe testing

Before executing or delegating any test/check/benchmark (including retries), apply `docs/WORKING-LOOP.md#desktop-safe-test-execution`: inspect transitive desktop effects; prefer non-disruptive tests; unknown or disruptive effects require a verified isolated runner or explicit per-run human authorization before execution. Never self-authorize or bypass the consumer guard. Continue safe work; unavailable mandatory evidence stays NOT_RUN / INCONCLUSIVE and blocks approval/merge.

## Procedure
1. **Read-only preflight:** confirm PR is `IN_REVIEW`/reopenable `CLOSED_UNMERGED`, not unfinished implementation, and inspect current owner/claim without acquiring it. Re-fetch exact head. The executable `pr:<N>` claim is acquired only after the single remediation-plan approval below; do not hold a lock during a human decision.
2. Collect every unresolved thread, blocking past finding and failing required check; check against **current code**. Group duplicate symptoms by root cause without omitting independently material defects.
3. Assign each exactly one disposition and proof:
   - **should fix** — valid in-scope defect, regression or required missing evidence;
   - **improvement** — non-blocking; make optional, normally defer unless user elects to include;
   - **discard** — duplicate, obsolete or factually wrong, with source proof;
   - **disagree** — evidence-based non-blocking difference; reply and leave review authority to reassess;
   - **push back** — an unresolved reviewer/owner decision; don't silently choose.
4. **Single gate:** show one complete decision table: finding/thread/CI link, proposed disposition, root cause, planned files and fix, tests, optional changes, open authority blockers and exact head. Ask **"Apply this plan? (yes/no)"** only when not already explicitly authorized for this exact snapshot. On no, perform no code/reply/thread mutations; no claim was acquired. Do not seek approval for each comment.
5. **Claim after approval, then edit:** atomically acquire the PR claim after approval; on yes, recheck exact head and governing authority. Set `PHASE=process-review`, `NUMBER=<PR number>` and run `python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" begin --repo "$REPO" --phase process-review --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"` against the configured shared host DB/worker identity (see `docs/WORKING-LOOP.md`). Accept only `ACQUIRED` or same-worker `RESUMED`, then invoke the same command with `verify` and require `VERIFIED` before `needs:processing` → `pr:processing` and each edit/push/thread/reply mutation. On `BUSY`/`DENIED`/`ERROR`, never write, steal or create a replacement PR. Fix accepted `should fix` root causes **and sibling instances** on the existing branch. Include approved improvements only when in scope and not delaying mandatory closure. Run targeted + risk/required checks; never weaken existing criteria. If an authority blocker remains, safely fix independent approved items then report what waits.
6. Push only approved and verified remediation to same PR; record old/new SHA and exact evidence. Reply once per relevant thread with rationale and test proof; resolve threads only where materially addressed and project permissions allow. `disagree`/`push back` are not self-closed as "fixed."
7. Re-inventory full current review/CI state and each ledger row: FIXED, SUPERSEDED_WITH_PROOF, BLOCKED, or DEFERRED_NONBLOCKING. Re-verify the executable claim before the final transition. When mandatory blockers are fixed and review authority can reassess outstanding disagreements, transition `pr:processing` → `needs:review`, then invoke `python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" release --repo "$REPO" --phase process-review --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"` and route to **full** `pr-review` of exact new head. Otherwise report BLOCKED, preserve the same candidate and token for same-worker continuation; release only on authorized cancellation/handoff, never abandon a claim or create a second PR.

## Output contract
PR/current revision; complete disposition + root-cause ledger; single approval response; before/after head; files/tests/CI evidence; comment/reply/thread actions; remaining blockers; label stage and next action.

## Handoff
Resolved batch → `pr-review`; incomplete accepted feature work → `implement-issue`; unresolved decision → named authority and keep same PR; follow-up IMPR → separate issue only with project authorization.
