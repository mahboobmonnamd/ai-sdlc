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
Fresh issue and DoR, accepted requirements/decisions/plan revision (where required), dependencies, security controls, ownership/claim adapter, candidate inventory including closed-unmerged PRs, current code/tests and project CI policy. See `docs/WORKING-LOOP.md` for states and claim guarantees.

## Provisional contract lane
AI-SDLC does not grant architecture or security authority. When consuming-project policy explicitly permits parallel implementation, a pending architecture/security review or unresolved normative choice does not by itself block reversible implementation. The owning issue must name each provisional contract, the accepted baseline and revisions, selected interim value, unresolved alternatives and decision owner, affected surfaces, rollback/replacement path, tests, fail-closed/disabled behavior, and an explicit acceptance-before-merge gate.

Proceed only on parts whose boundary and failure behavior are testable. Never contradict accepted authority, expose an unreviewed permission or privacy path, make an irreversible migration, silently truncate or lose user data, or enable a capability whose safety depends on the unresolved decision. Isolate dependent behavior behind a tested boundary and keep it disabled; continue independent work. Mark code, evidence and PR claims as provisional. Implementation and independent architecture/security review may run concurrently.

A provisional candidate may be published and technically reviewed, but it is never merge-ready while a required contract decision remains unresolved. Before merge, resolve every recorded decision through the consumer's authority process, reconcile the implementation and tests against the accepted result, rerun affected checks, and obtain required exact-head review. Technical PR approval does not accept an ADR/specification. Packaging, distribution signing, and production qualification are separate gates; require them before implementation only when governing project authority explicitly says the source change itself requires them.

## Stop or escalate when
Other owner/candidate, unclear or rejected stage, material unsatisfied DoR/dependency/authority that is not explicitly and safely provisional, missing atomic claim for new work, mandatory tests failing/unavailable, or approval tied to a changed governing snapshot. If only a separable contract decision is unresolved, record it as provisional, block/disable dependent behavior, and continue independent accepted work.

## Procedure
1. **Read-only preflight:** fetch issue and its revision, candidate/branch links including closed-unmerged and merged content, claims, open concerns, dependent work and trusted sources. Determine NEW vs RESUME. If IN_REVIEW route to `process-review` for feedback; if UNKNOWN or duplicate owners/candidates stop. If work is partially implemented and owned, keep it in this skill even when CI/early feedback exists.
2. **Ready + plan:** assess all 12 DoR checks (verification command optional). Validate the existing 3–7-step plan against actual code seams, tests, dependencies, risks, rollback/compatibility and accepted architecture. Map AC → intended test; avoid a second plan-acceptance ceremony. If project policy requires a separate approved plan, load its **exact accepted revision**. Do not silently alter decisions; refer gaps to `create-issue`.
3. **Gate 1:** show readiness table (collapsed passes allowed), proposed files/steps, tests, material risks and exact issue/plan revision. A direct user instruction that explicitly authorizes implementation of this issue and scope satisfies Gate 1; do not ask again. Otherwise ask **"Proceed with implementation? (yes/no)"**. On no stop without ownership claim, branch or edits. For an unchanged previously approved resume, reuse the saved approval; otherwise show material delta and re-ask.
4. **Claim:** after yes, re-fetch issue/decisions/dependencies, atomically acquire exclusive `issue:<N>` ownership or verify existing owned claim. On collision stop. Re-read token/owner, then transition `needs:implementation` → `issue:implementing`; do not edit on failed transition until reconciled.
5. **Branch:** NEW → fetch `origin/main` and branch from its exact SHA (unless explicit authorized stack/dependency policy selects another base); RESUME → existing authorized head, including reopenable closed-unmerged PR. Never create a replacement merely because work spans sessions. Persist candidate stage `IMPLEMENTATION_IN_PROGRESS`.
6. **Implement with feedback:** write the smallest coherent production-intent code and tests; use a failing test when useful. After each root cause, run narrow checks. Include relevant negative, boundary/security, migration/recovery, concurrency, compatibility and integration coverage proportional to actual risk. Keep provisional behavior isolated, fail-closed and disabled; do not merge it while its decision is unresolved. Unrelated findings become separate issues, not changes in this PR.
7. **Verification:** run required project checks and risk-driven evidence on the finished candidate. Record exact local revision, commands/results and every criterion PASS/FAIL/INCONCLUSIVE, including each provisional decision and its remaining merge gate. Pre-PR self-review the entire diff for scope, test weakening, missing failure paths, API/docs claims and secret exposure. An unrun mandatory check is not passing; do not offer Gate 2 while mandatory evidence is failing.
8. **Gate 2:** display branch/base/head, diffstat, full acceptance→evidence matrix, check results, residual risks and **complete PR title/body** (`Closes #N`, summary, test proof, limits). Ask **"Push branch and create PR? (yes/no)"**; no push/PR on no. Previously approved unchanged candidate may resume without another prompt.
9. **Publish:** verify same issue scope, claim, approved diff/head and base. Push exactly that branch; create or reuse one non-draft PR; apply PR `needs:review`, persist `IN_REVIEW`, mark issue `issue:in-review` (or project equivalent) and release implementation claim conditionally. Record link and actual remote head. CI can run after push: report pending/failing remote status honestly. Label provisional decisions and link the required authority review; a pending decision keeps the PR blocked from merge. Never automatically approve or merge.

## Output contract
Mode NEW/RESUME; issue/current revision; candidate/stage/owner; DoR + validated plan; both gate decisions; exact branch/base/head; changed files/diffstat; AC→evidence table with commands and results; risks/unknowns; PR body/URL, remote CI and next action. Distinguish NOT_RUN from PASS.

## Handoff
PR opened → `pr-review` once evidence is available. Existing unfinished scope → resume `implement-issue`. Reviewed feedback → `process-review`. DoR or accepted authority gap → `create-issue` or decision owner. No duplicate candidate creation.
