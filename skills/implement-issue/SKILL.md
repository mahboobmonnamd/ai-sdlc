---
name: implement-issue
description: Resume or deliver one ready issue from accepted plan to verified PR through two human gates; not for review-stage remediation or merge.
---

# Implement issue

## Invocation contract
`/implement-issue <Issue>`; exact issue number is mandatory. Use existing project repository; never infer the issue number.

## When to use
New `needs:implementation` work or an authorized partial implementation on the **same branch/candidate**.

## Do not use
Do not claim from labels alone, invent design choices, run another owner's branch, create duplicate PRs, weaken checks, perform unrelated cleanup, or push without Gate 2.

## Required context
Start with the issue's problem and relevant code/tests. Read `docs/WORKING-LOOP.md#task-first-execution-and-progressive-context`, applicable authority/claim/state sections, exact issue/plan revision, ownership, candidate inventory (including closed-unmerged), affected dependencies and applicable CI. Do not preload unrelated skills or docs.

## ADR authority

Read `docs/WORKING-LOOP.md#adr-lifecycle-merge-is-acceptance` only when an ADR governs or changes: merged authority binds; an ADR's own final reviewed PR accepts at merge, external prerequisites must be accepted. Do not treat a qualification plan as proof.

## Provisional contract lane

Only use the explicitly consumer-authorized bounded lane in `docs/WORKING-LOOP.md#bounded-provisional-contract-lane`. Record the exact provisional decision, baseline, owner, rollback, affected surface, tests and acceptance gate. Keep uncertain behavior isolated, disabled/fail-closed; no irreversible or unauthorized change. Continue independent work; no merge until external authority and required evidence are resolved.

## Stop or escalate when
Other owner/candidate, unclear or rejected stage, material unsatisfied DoR/dependency/authority that is not explicitly and safely provisional, missing atomic claim for new work, mandatory tests failing/unavailable, or approval tied to a changed governing snapshot. If only a separable contract decision is unresolved, record it as provisional, block/disable dependent behavior, and continue independent accepted work.

## Desktop-safe testing

Apply `docs/WORKING-LOOP.md#desktop-safe-test-execution` before any test or delegation: prefer non-disruptive or verified isolated execution; disruptive runs require explicit per-run human authorization when permitted. Never self-authorize. Unknown effects fail closed. Reuse only proven unaffected evidence; rerun required affected/exact-head checks. Unavailable mandatory evidence is NOT_RUN / INCONCLUSIVE; escalate, do not bypass.

## Procedure
1. **Read-only preflight:** fetch issue and its revision, candidate/branch links including closed-unmerged and merged content, claims, open concerns, dependent work and trusted sources. Determine NEW vs RESUME. If IN_REVIEW route to `process-review` for feedback; if UNKNOWN or duplicate owners/candidates stop. If work is partially implemented and owned, keep it in this skill even when CI/early feedback exists.
2. **Ready + plan:** assess applicable DoR checks (verification command optional); reuse the issue's lane and reclassify on new risk. Validate the existing proportional plan against actual code seams, tests, dependencies, risks, rollback/compatibility and accepted architecture. Map AC → intended test; avoid a second plan-acceptance ceremony. Apply `docs/WORKING-LOOP.md#review-convergence-and-evidence-reuse`: independent read-only plan challenge for high-risk/material multi-component work, routine author plan validation otherwise unless consumer policy requires more; record findings in existing Gate 1 and resolve material gaps before edits. If project policy requires a separate approved plan, load its **exact accepted revision**. Do not silently alter decisions; refer gaps to `create-issue`.
3. **Gate 1:** show compact readiness, proposed files/steps, tests, material risks and exact issue/plan revision; LIGHTWEIGHT needs only intent, applicable check and exceptions. A direct user instruction that explicitly authorizes implementation of this issue and scope satisfies Gate 1; do not ask again. Otherwise ask **"Proceed with implementation? (yes/no)"**. On no stop without ownership claim, branch or edits. For an unchanged previously approved resume, reuse the saved approval; otherwise show material delta and re-ask.
4. **Claim:** after yes, re-fetch issue/decisions/dependencies. Set `PHASE=implement`, `NUMBER=<issue number>` and invoke `python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" begin --repo "$REPO" --phase implement --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"` using the **host-configured** common `AI_SDLC_CLAIM_DB` and stable `AI_SDLC_WORKER_ID` (see `docs/WORKING-LOOP.md`). Only `ACQUIRED` or `RESUMED` permits continuing. Invoke the same command with `verify` (rather than `begin`) and require `VERIFIED` before the issue-label transition, branch/edit, push and PR publication. An atomically acquired claim must be `VERIFIED` before changing `needs:implementation` to `issue:implementing`. `BUSY`/`DENIED`/`ERROR` prevents those writes; report the owner when available, never fall back to labels or replace the candidate. A same-worker resume reuses its existing private token file without acquiring a second claim.
5. **Branch:** NEW → fetch `origin/main` and branch from its exact SHA (unless explicit authorized stack/dependency policy selects another base); RESUME → existing authorized head, including reopenable closed-unmerged PR. Never create a replacement merely because work spans sessions. Persist candidate stage `IMPLEMENTATION_IN_PROGRESS`.
6. **Implement with feedback:** follow the task-first engineering loop: trace actual behavior, reproduce defects when feasible, implement the smallest coherent production change, and verify observable acceptance at the real affected boundary. After each root cause, run narrow checks. Include relevant negative, boundary/security, migration/recovery, concurrency, compatibility and integration coverage proportional to actual risk. Keep provisional behavior isolated, fail-closed and disabled; do not merge it while its choice is unresolved or its external ADR prerequisite is unmerged. Unrelated findings become separate issues, not changes in this PR.
7. **Verification:** run required project checks and risk-driven evidence on the finished candidate. Record exact local revision, commands/results and every criterion PASS/FAIL/INCONCLUSIVE, including each provisional decision and its remaining merge gate. Pre-PR self-review the entire diff for scope, test weakening, missing failure paths, API/docs claims and secret exposure. An unrun mandatory check is not passing; do not offer Gate 2 while mandatory evidence is failing. Do not commission separate independent preflight by default. If the consumer requires developer-owned independent preflight, use the canonical convergence ledger, initial full review, batched fixes, focused rechecks and final independent exact-head whole-candidate review before readiness. Stop and escalate after 3 routine remediation cycles or earlier triggers; no new automatic budget at formal review. Keep formal review separate and no self-approval. Do not launch repeated full reviews on unfinished code or missing mandatory evidence.
8. **Gate 2:** display branch/base/head, diffstat, existing acceptance→evidence packet (compact for LIGHTWEIGHT), check results, residual risks and **complete PR title/body** (`Closes #N`, summary, test proof, limits). If the current user instruction already explicitly authorizes publication of this exact scope and candidate, record it without asking again. Otherwise ask **"Push branch and create PR? (yes/no)"**; no push/PR on no. Previously approved unchanged candidate may resume without another prompt.
9. **Publish:** re-verify the *same* executable claim and approved issue scope, diff/head and base. Push exactly that branch; create or reuse one non-draft PR; apply PR `needs:review`, persist `IN_REVIEW`, mark issue `issue:in-review` (or project equivalent). Only after these writes and a confirmed handoff, invoke `python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" release --repo "$REPO" --phase implement --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"`. A failed handoff retains the same claim/token for continuation; do not abandon the lock silently or create another PR. Record link and actual remote head. CI can run after push: report pending/failing remote status honestly. Label provisional decisions and link the required authority review; a pending decision keeps the PR blocked from merge. Never automatically approve or merge.

## Output contract
Update the shared record with issue/revision, NEW/RESUME, candidate/owner, readiness, applicable plan/gates, branch/base/head, diffstat, AC→evidence, risks, PR URL/CI and next action. Show the complete PR body at Gate 2; otherwise link rather than repeat. Distinguish NOT_RUN from PASS.

## Handoff
PR opened → `pr-review` once evidence is available. Existing unfinished scope → resume `implement-issue`. Reviewed feedback → `process-review`. DoR or accepted authority gap → `create-issue` or decision owner. No duplicate candidate creation.
