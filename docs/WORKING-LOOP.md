# AI-SDLC canonical working loop

Normative operating rules for all active skills. Design rationale and performance goals: [SDLC-DESIGN.md](SDLC-DESIGN.md).

## Task-first execution and progressive context

Start with the user's problem, expected outcome and evidence. Inspect affected code and reproduce defects before choosing a solution. The workflow is a guardrail, not a substitute for engineering judgment. Do not invent acceptance, require a new ADR or expand scope without a material need.

Load only the active skill, applicable policy sections (read the named heading/range, not the whole file), consumer overrides, issue/PR and relevant authoritative sources. Use targeted symbol/file search; expand on material uncertainty. Do not preload this entire document, every skill, historical PRD/Phase-0, all ADRs or the whole repository. Reuse unchanged context and source links; revalidate changed/stale authority and facts affecting safety or correctness. Never omit relevant requirements or hidden effects.

### Risk-proportional rigor

Select a lane by actual impact, record a one-line rationale in the existing issue/PR or evidence (no new gate, artifact or label), and reclassify as scope or risk changes. Unknown risk is STANDARD or CRITICAL until resolved. Consumer requirements can demand greater rigor.

| Lane | Scope | Plan / verification / review |
| --- | --- | --- |
| LIGHTWEIGHT | Non-normative typo/copy/formatting or demonstrably behavior-preserving bounded change; no contract, executable config, authority, security or dependency impact | Short intent, scope, observable check; one obvious action or 1–3 steps. Applicable deterministic checks and one independent review covering the entire small candidate; no separate preflight/specialist unless required |
| STANDARD | Normal bounded feature/fix | Concise expected behavior, material negative cases, non-goals/dependencies, targeted unit/integration/regression and required CI; one independent whole-candidate review |
| CRITICAL | Security/privacy/auth, migration/data loss, architecture/normative ADR, concurrency, public protocol/API compatibility, release/CI policy, high blast radius or material multi-component uncertainty | Explicit invariants, authority, rollback, independent plan challenge, applicable specialists and adversarial/negative/integration evidence; qualification where governing merge policy requires it |

Every lane preserves accepted authority, ownership, user authorization, production intent, applicable tests, independent exact-head approval and branch protections. Small diffs and documentation extensions alone do not establish low risk. Do not add irrelevant tests, specialist reviews, ADRs or ceremonies because a template mentions them.

### One evidence packet, one accountable review

Keep one compact, durable candidate record in the existing issue/PR or authorized host state: intent/criteria, lane, head/base, authority links, affected boundaries, checks/results and provenance, blockers/dispositions and next action. Reuse it through verification, review and merge; independently validate provenance and rerun affected or required checks. Prefer existing executable CI/lint/schema/build checks over repeated model checks; never invent PASS or substitute text checks for behavioral evidence. Missing required evidence blocks.

A review may find zero issues. No comment quota, speculative defects or style preferences as blockers. Cite concrete failure, accepted contract, required evidence gap or substantiated material risk for every blocking finding. APPROVE when required evidence and full applicable review pass; no second review of the same approved head. Author self-review and one independent review suffice unless the consumer explicitly requires additional preflight; reuse validated preflight evidence. Formal independent approval remains mandatory. After failure, batch findings, recheck impact and finalize together where possible; keep exact-head and escalation safeguards.

## 12-point Definition of Ready

Assess applicable checks; report material FAIL/UNKNOWN and justify material N/A. For LIGHTWEIGHT, report the short intent, scope, check and exceptions; no mandatory twelve-row table. For STANDARD/CRITICAL use a compact readiness summary, expanding only where needed. Only item 5 (the command) is optional when applicable; an irrelevant check may be N/A with a concise rationale. Material FAIL or UNKNOWN is blocking unless the issue explicitly records a safe provisional contract under the lane below; a provisional decision is never treated as accepted.

| # | Check | PASS means |
| --- | --- | --- |
| 1 | Problem stated | Outcome, user/affected system and why |
| 2 | Observable behavior | Concrete current vs expected behavior and material negative cases |
| 3 | Bounded scope | In scope/out of scope; independently reviewable |
| 4 | Verifiable acceptance | Testable, externally observable pass/fail criteria |
| 5 | Verification command (optional) | Useful known command specified; if absent, expected evidence still named |
| 6 | Design decisions closed or explicitly provisional | Decisions under `## Design nuance` are accepted or explicitly provisional under the bounded lane; relevant open `!+concern` blocks unless it meets every provisional-lane requirement |
| 7 | Congruence | Compatible with accepted product intent, architecture and code ownership |
| 8 | Dependencies | Named, correctly ordered, satisfied or explicitly gated |
| 9 | Not duplicate | Search issues, open PRs, merged changes and candidate branches |
| 10 | Self-contained | Issue + resolvable authoritative links suffice without private conversation |
| 11 | Implementation plan | One obvious action or 1–3 steps for LIGHTWEIGHT; concise ordered production steps for STANDARD/CRITICAL, with criterion-to-test map |
| 12 | Security controls | Trust boundaries, access, secrets, inputs, privacy and failure risks assessed; N/A justified |

DoR is an **outcome contract**, not an excuse for bureaucratic prose. A sufficient issue is its own plan. An external versioned plan is required only if project policy explicitly demands it. Load its exact accepted revision; a merely proposed plan cannot authorize changes. A coordination-only label or timestamp edit does not invalidate accepted scope; changed behavior, dependencies or decisions do.


## ADR lifecycle: merge is acceptance

An Architecture Decision Record (ADR) is proposed while its introducing or changing PR is unmerged. An authorized merge into the repository's designated authoritative branch (normally the default branch) is the acceptance event for the exact ADR content merged. ADRs on that branch are accepted; no separate status field, proposed-to-accepted edit, follow-up acceptance PR, or second approval ceremony is required. Legacy status text is non-authoritative and should be removed when touched; a stale "Proposed" label cannot block a merged ADR, and an "Accepted" label cannot make an unmerged ADR authoritative. Closed-unmerged PRs do not accept anything.

The ADR PR must receive the applicable independent architecture/security review and satisfy normal merge gates. Review approval makes the ADR eligible for authorized merge, not accepted before merge. A decision PR can be approved and merged to establish its own authority: do not require the very ADR it introduces to be accepted beforehand. If a PR also implements the decision, review the final decision, implementation, tests and safety together under the same merge gate; no unresolved choice or unaccepted *external* prerequisite may be smuggled in. For a separate dependent PR, require the governing ADR merge on the authoritative branch, reconcile the actual merged content, and rerun affected verification/review. An ADR merged only to a feature branch is not accepted.

Resolve authority from the authoritative branch revision and, when needed, verified merge evidence (PR URL, merge commit and exact file content), not labels, agent memory or local copies. A merged ADR that chooses a future qualification process accepts that process, not the unmade choice or a passing qualification result. Do not invent unresolved choices, mark release/security/qualification gates passed, or silently change established decisions. Change or supersede an ADR through a new reviewed PR; the existing merged decision governs until that PR merges. Preserve historical provenance and identify the effective successor. This rule is specific to ADRs; other approvals and acceptance gates retain their own authority contracts.

## Bounded provisional contract lane

A consumer may authorize implementation before a separate architecture/security review finishes only when its policy explicitly permits this lane and the issue records the accepted baseline/revisions, the exact provisional contract and selected interim value, unresolved alternatives and decision owner, affected surfaces, reversibility/rollback, tests, fail-closed or disabled behavior, and acceptance-before-merge gate. This lane does not let an issue, plan, skill, or agent change accepted authority.

Proceed only on testable, isolated behavior. Continue independent work when one surface is blocked. Do not expose new authorization/privacy behavior, make irreversible data changes, hide or truncate failures, or enable a feature whose safety depends on the pending decision. A provisional candidate may be published and independently reviewed while architecture/security review runs. Technical review does not accept the contract; for an ADR, authorized merge is acceptance.

An unresolved provisional decision is a mandatory merge blocker. Before a dependent merge, the decision must be resolved by its governing authority (for an external ADR, verify its authorized merge); implementation and tests must be reconciled with that outcome and affected verification rerun. An ADR-bearing PR may establish its own final decision at merge under the ADR lifecycle above. Distribution signing and other release qualification remain separate unless authoritative project policy explicitly requires the artifact before source work.

## Correct candidate stage

`NONE | IMPLEMENTATION_IN_PROGRESS | IN_REVIEW | CLOSED_UNMERGED | REJECTED | UNKNOWN`.

- `NONE` → only new ready work; check duplicate branches/PRs before creating anything.
- `IMPLEMENTATION_IN_PROGRESS` → continue the **same** authorized branch/head, including incomplete scope, early feedback or failing CI.
- `IN_REVIEW` → review/processing; do not add unfinished unrelated feature work.
- `CLOSED_UNMERGED` → inspect and reopen/resume same head with authority; do not fork duplicate work.
- `REJECTED` → do not resume without a new approved decision.
- `UNKNOWN` or multiple candidates/owners → stop, reconcile ownership and stage before mutation.

Persist stage, candidate identity, issue link and responsible actor in durable host/project state. Reconstruct from current source when possible; no invented lifecycle labels or stale memory.

## Label transitions (state display, never a lock)

```text
issue needs:implementation
  --[Gate 1 approved + exclusive claim]--> issue:implementing
  --[verified PR opened]--> issue:in-review (PR: needs:review)
PR needs:review --[review claim]--> pr:reviewing
  --[REQUEST_CHANGES]--> needs:processing
  --[APPROVE]--> needs:merge
PR needs:processing --[processing claim]--> pr:processing
  --[approved batch + evidence]--> needs:review
PR needs:merge --[exact-head checks, protections]--> MERGED
```

Transitions are mutually exclusive per resource and retried idempotently: add destination then remove only applicable old label; reconcile on partial failure. Keep linked issue open until target-branch merge actually closes it via `Closes #N`. `issue:in-review` avoids mistakenly returning submitted work to the ready backlog; if the project lacks this label, retain equivalent durable association and record it explicitly.

## Exclusive ownership

A claim requires a project-configured **atomic compare-and-set/create-if-absent** backend, not GitHub label/assignee read-then-write. It must handle issue implementation and **one shared PR exclusion domain** for reviewing/processing, and expose owner, unique token, acquire/recheck, conditional release and audited recovery. Git reference creation may be used for atomic first acquisition but **is not a complete reusable lock** unless safe owner-checked transitions/release are implemented; do not delete a ref based only on a stale read. A failed or unavailable required claim blocks mutations.

**Timing:** read-only eligibility/DoR/plan preflight → Gate 1 → revalidate snapshot → atomic acquire and confirm → issue label swap → branch/edit. This prevents locking an issue while waiting on a human. An authorized in-progress resume validates the existing claim; do not lose continuity on a label mismatch. Recheck token before push, review submission, thread resolution and merge where required. Never replace another owner's claim automatically. If the owner is unavailable, flag for authorized recovery.

### Executable local claim gate (single-host reference adapter)

The active `implement-issue`, `pr-review` and `process-review` skills MUST use an executable host claim gate, not the GitHub label or assignee. The reference adapter is `tools/workflow_claims.py` in the **pinned AI-SDLC checkout**. The consuming host sets the following before any mutation:

- `AI_SDLC_TOOL_ROOT`: absolute path of that pinned checkout, never an assumed relative path in the consuming repository.
- `AI_SDLC_CLAIM_DB`: one stable, private, **local** SQLite path shared by all workers/worktrees on this host. The directory must be owned by the current user and mode 0700. Never use a per-worktree DB or claim distributed-host exclusivity.
- `AI_SDLC_WORKER_ID`: host-established identity **unique across concurrently active workers** and stable only for authorized single-worker resume. The Python CLI does **not authenticate identities** or prevent a second live process with the same owner and token file from passing `verify`; the host must prevent concurrent reuse and control mutation permissions.
- `AI_SDLC_CLAIM_TOKEN_FILE`: unique, private 0600 token-file path for this worker **and resource**, outside the repository and retained across restarts until the handoff/release.

After read-only eligibility and the applicable pre-mutation user gate, run the exact form:

```sh
python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" begin --repo "$REPO" --phase "$PHASE" --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"
python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" verify --repo "$REPO" --phase "$PHASE" --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"
# Only after a completed handoff/cancellation, not while an owned task is still being worked:
python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" release --repo "$REPO" --phase "$PHASE" --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"
```

Use `PHASE=implement, NUMBER=issue number` for implementation; `PHASE=review` or `process-review`, `NUMBER=PR number` for reviewing/remediation. Both PR phases map to **one** `pr:<N>` claim namespace. A clean `begin` returns `ACQUIRED`, a same-worker resume returns `RESUMED`; both exit zero. A successful `verify` returns `VERIFIED`. No mutation is permitted without `ACQUIRED`/`RESUMED` followed by `VERIFIED` for the same resource/worker. `BUSY` or `DENIED` exits 1; tool/config errors exit 2. Never treat either as successful or create another candidate to bypass it.

**Re-verify immediately before** each label/branch/edit/push, review submission, review-thread resolution or handoff mutation; verify new GitHub head/approval separately. Resume the existing authorized token file for the same worker. A missing token for an already-held claim requires authorized recovery, not an automatic reset. Release only on successful publication/review handoff or deliberate cancellation; preserve it across session interruption and while the same worker is fixing unfinished work. Do not acquire claims merely to wait for an initial human plan/remediation approval. After implementation has begun, keep its existing claim through the publication gate to prevent a second worker editing the unfinished candidate; release only after an authorized cancellation or completed handoff.

If the host cannot run this pinned CLI or provide a different *proven atomic* backend, report exactly the missing capability and continue read-only analysis/tests where possible. **Do not** substitute a label, infer the worker's identity, use per-agent ephemeral DBs, or claim a completed production integration. Real agent-host enforcement at every mutation remains a consumer integration step.

## Four user decisions, no ritual approvals

| Moment | Display | Ask |
| --- | --- | --- |
| New/refined issue | Final issue body + DoR evidence | Approve creation/update? |
| Implement Gate 1 | DoR readiness, exact issue revision, short plan, testing/risk strategy, provisional decision ledger | Ask only if current user instruction does not already authorize this exact implementation |
| Implement Gate 2 | diffstat, exact branch/base/head, acceptance-to-evidence matrix, provisional blockers, self-review, complete PR title/body | Ask only if current user instruction does not already authorize publishing this exact work |
| Process-review | All actionable findings+CI, dispositions, file/test impact, unresolved authority | **Apply this plan? (yes/no)** unless already authorized for exact batch; escalation requires a new bounded decision |

The approval applies to a **specific snapshot**. If materially changed requirements, plan or reviewed diff invalidate an approval, show only the material delta and seek an updated decision (not a blanket repeat). A no means no corresponding action; do not pretend work happened. Explicit `/pr-merge <PR>` already authorizes a merge attempt, subject to mandatory checks. Direct authorization for implementation or PR creation never implies merge authorization.

## Desktop-safe test execution

Applies to every skill, agent, delegated worker, test command, benchmark, automation tool and retry, including local verification, review, remediation and CI. **Non-disruptive by default**: do not take over a human's active desktop as a side effect of engineering work.

- Before executing a command or delegating it, inspect the actual runner, configuration and transitive scripts for desktop effects. Prefer deterministic unit, integration, API, component, offscreen rendering and headless browser tests in isolated environments. A test named "unit", "check", "test" or "headless" is not evidence of safety. Unknown desktop effects are not permission to run. Resolve uncertainty by read-only inspection or a verified containment environment; do not ask for blanket interactive authorization of an unknown command.
- Desktop-affecting operations include foreground app activation/focus changes, global keyboard/mouse input, window management, screen capture of the user's desktop, display/session changes, and any native or browser automation that can interfere with unrelated apps. A separate process, worktree, app instance or runtime namespace is not desktop isolation.
- Run desktop-affecting tests only on a verified, designated isolated test host/session (such as dedicated test hardware, VM, or isolated CI runner) or with **explicit per-run human authorization** for a known bounded suite on the active desktop, only when consumer policy permits interactive execution. Authorization must identify the host/session, intended suite or bounded scope, and interruption/time limit, candidate revision, runner entrypoint and permitted retry count (default zero). General implementation, test, review, merge or plan approval does not grant this permission; a generic CI flag, inherited environment variable, prior authorization for a different run or agent-created opt-in is not proof. Do not request approval when an appropriate isolated runner is already authorized and available.
- Consumers must separate safe default commands from explicit headed/full commands, fail closed at disruptive runner entrypoints before side effects, serialize exclusive desktop use across workers/worktrees, bound execution and retries, and clean up only test-owned resources on exit/interruption. Do not disable user controls, alter unrelated apps or escalate privileges to obtain desktop access. The agent must not set or bypass a consumer's authorization guard on its own.
- If a required test cannot safely run, continue independent safe work, use an authorized isolated runner if available, and report the exact unrun test, reason and next action as NOT_RUN / INCONCLUSIVE. Never silently drop coverage, weaken assertions, replace real native interaction or hardware evidence with an unsuitable simulation, or mark skipped evidence PASS. Required evidence remains a review/merge gate. Permission is a conditional safety requirement for a disruptive run, not a new routine SDLC approval gate.
- Record the exact command, revision, execution class (non-disruptive / isolated / authorized interactive), relevant host/runner and result. For an interactive run record scope and authorization provenance, without capturing private desktop contents. Stop when the approved scope or time limit is reached, on human interruption, or on loss of isolation/authorization; no unapproved retry or continuation. Require fresh authorization for another interactive run, including a changed candidate or a new review cycle. A pre-authorized batch may include explicitly bounded suite steps and retries, but not future unspecified rounds.

This is a generic agent/consumer contract, not an OS-level sandbox or automatic authorization mechanism. Each consuming project owns its test inventory, platform-specific enforcement, isolation and evidence. An agent that cannot establish safety must not execute the potentially disruptive command.

### Interaction with review convergence

- During existing Gate 1, identify relevant test classes and execution constraints; maintain a consumer-owned test inventory covering transitive effects, required fidelity, isolated runner capability and applicable evidence. Prefer app-scoped automation, offscreen/headless/API testing and isolated disposable state. A runner is isolated only if its actual display/input/session and test resource boundaries prevent interference with the active user; a VM or CI label alone is not proof. Never authorize or intercept the user's desktop to satisfy a test convenience.
- Use safe narrow tests during implementation/remediation and batch required expensive native/headed suites at risk-appropriate checkpoints. Run a mandatory suite when affected by code, contract, fixtures, toolchain or environment changes, or when required at the exact head by governing policy. A review stage is not itself a reason to launch another interactive run. Reuse unchanged historical headed evidence only under [review convergence and evidence reuse](#review-convergence-and-evidence-reuse), with independent equivalence of relevant runner class, display/input isolation, device/OS versions where relevant, suite/config and dependencies; never claim a previous run executed at the new head or reuse its desktop authorization.
- Coordinate specialists so the implementation worker or designated runner executes a shared required suite once per qualifying snapshot, subject to independent reviewer verification and any mandated independent rerun. No reviewer, delegated worker or merge skill may start a duplicate desktop suite on its own. A genuine affected or mandated exact-head rerun remains mandatory and needs the same safety checks and new interactive permission if applicable. Final independent whole-candidate review still required; focused recheck cannot approve.
- On unavailable isolation, missing permission, unsafe command or repeat failure, record exact blocked evidence and escalate under the three-cycle/early-stop policy; continue only separable safe work. Do not spin waiting for a desktop, relaunch identical failed suites, switch hosts or downgrade tests to make a PR ready. No automated fourth remediation cycle and no quality waiver. Human desktop permission is separate from any remediation/plan approval and cannot be inferred from an approved retry budget.
- Consumer adoption must qualify both permitted and denied execution paths: unsafe default command, transitive runner, two-worker contention, time limit/cancellation and test-owned cleanup, revoked/expired/wrong-scope authorization, no desktop access from headless mode and correctly isolated native interaction. Validate evidence reuse/invalidation and no duplicate invocation. Record missing platform capabilities as NOT_RUN, not as a sandbox guarantee.

## Verification and merge

- Every mandatory acceptance criterion must show exact test/measurement/demonstration, observed result and revision. Evidence `PASS/FAIL/INCONCLUSIVE`; unrun is not PASS.
- Use narrow tests during coding and broader risk-driven evidence before Gate 2: normal path, negative/errors, auth/security, compatibility, concurrency/lifecycle, storage/migration/recovery, performance/operability only where relevant.
- Verify final local diff has no hidden debug changes, unrelated scope, test weakening, secret exposure, temporary production substitute or unchecked migration.
- A technical review may assess a safely isolated provisional candidate while decision review proceeds; its verdict must remain conditional and cannot count as authority acceptance.
- Any unresolved choice or unaccepted external provisional contract listed in the issue/PR blocks merge, even when code review and CI pass. Resolve the decision and rerun affected tests/checks before exact-head merge review. The final reviewed ADR in the same PR is accepted by that PR's authorized merge, not a separate status change.
- After push, CI and GitHub review status are **fresh again**. Pushing and opening a PR is not merge readiness. Review against exact current PR head + base; stale approval is not valid. Respect code owners, required checks, merge queue, blocking threads, rulesets and current permission. No branch-protection bypass.
- `[CRIT]`, `[SEC]` and `[NONCONF]` block approval when materially unresolved. `[IMPR]` is non-blocking; `[GOOD]` is positive evidence. Findings need file/line when applicable, failure mechanism and an actionable correction.
- `process-review` handles review stage only; classify every finding as should fix / improvement / discard / disagree / push back. A justified disagreement can clear an invalid blocker only through a new independent reviewer decision; the implementer cannot approve their own resolution.

## Review convergence and evidence reuse

Applies to developer-owned independent preflight (where consumer requires it) and formal review/remediation. Preserve separate formal non-author approval, project protections and explicit merge authorization. A preflight reviewer is read-only, independent of implementation, reviews a frozen candidate and never takes the implementer's mutation claim or posts formal approval. Consumers may require stricter review coverage, not weaker gates or unbounded automatic retries.

### Plan and initial full review

- At Gate 1 freeze scope, criterion-to-test map, authority/revisions, impacted boundaries, risks, verification and non-goals. For high-risk architecture/security/data/compatibility/concurrency or material multi-component changes, commission independent read-only plan challenge before implementation; resolve material gaps with decision owner. Routine low-risk work needs author plan validation unless consumer requires more. Record in existing plan/issue and Gate 1; no new human approval ceremony or generic plan artifact. Plan review is not code approval.
- Implement/test coherent vertical slices. Run narrow tests during coding, required applicable checks and author self-review before independent review. Do not commission full readiness reviews of unfinished scope, failing mandatory checks or unavailable mandatory evidence. Early specialist advice is optional and not a verdict.
- Start the first independent review with full candidate coverage of frozen head/base, acceptance, affected paths and required evidence; reuse validated preflight observations at formal review instead of repeating unchanged work, finish all material findings, including security, failures, compatibility and operational risks. Delegate risk-based specialist work only when useful; combine findings into one deduplicated ledger and accountable independent verdict, not competing approval loops. Specialist completion is not approval.

### Findings and bounded remediation

- Stable finding ID, root cause, affected boundary/criterion, severity, reproduction/evidence, owner, first/last seen head, disposition, fix/test and reviewer decision. Group duplicates and siblings without hiding independent defects. CRIT/SEC/NONCONF with demonstrated material failure, accepted-contract deviation or mandatory evidence gap block; IMPR is optional and never blocks alone. Defer unrelated improvements; no invented acceptance, preferred-refactor blockers or downgrade of valid findings to meet budget. New material regressions or missed real blockers still block.
- Batch confirmed blockers and required check failures under one authorized remediation snapshot; fix root causes and sibling instances, add regression tests, run targeted plus required broader checks before re-review. Never weaken tests, retrospectively lower thresholds or self-close a disputed blocker. Independent reviewer adjudicates.
- Count a routine remediation cycle when a complete blocker batch has been attempted and its updated candidate independently rechecked (including failed/no-progress attempts; an attempted batch blocked before recheck is recorded and escalated, not retried in a loop). Maintain one durable ledger per candidate across sessions, commits, reviewer agents, preflight/formal handoffs and label transitions; record stage for each entry. Do not reset budget by splitting batches, changing SHA, spawning agents or creating replacement PRs. Default maximum **3 routine remediation cycles per candidate convergence campaign**; consumer may explicitly lower it. No-progress or repeated root cause triggers root-cause investigation immediately. Second failed attempt on same root cause, identical repeat review with no relevant change, unresolved inconsistent reviewer findings, missing required evidence/authority, or unsafe/unbounded work triggers escalation even before cycle 3.
- If blockers remain after cycle 3 or early escalation holds, stop automatic review/fix recursion. Preserve same branch/candidate and existing claim until authorized handoff/cancellation (never acquire a new claim merely to await initial approval). Record BLOCKED/INCONCLUSIVE or REQUEST_CHANGES as appropriate; never APPROVE, mark ready or merge because budget expired. Escalation packet: head/base, cycle, open IDs, reproduction/root cause, attempted fixes and tests, changed risk, responsible owner, concrete next decision (targeted corrective plan, required environment, authority or explicit rescope). Only an authorized revised plan/additional bounded budget resumes same candidate with cumulative history; no silent reset or waiver. If all blockers close on cycle 3, final verification is permitted without another remediation authorization.

### Focused rechecks and final whole-candidate review

- Interim remediation recheck may focus on old-to-new diff, open findings, affected transitive dependencies/call paths, contracts, security/failure/compatibility boundaries and affected tests. Compare full candidate/base/authority and inventory whole diff first; conservatively assess impact. No delta-only approval. Unknown impact, changed authority/base semantics, core/security/shared interface changes, broad structure, contradictory evidence or regression expand to full review immediately. Stricter consumer full passes still apply; consolidate evidence and escalate rather than repeat indefinitely.
- Reuse prior unchanged observations/test evidence only after independent reviewer verifies provenance and equivalence: exact prior head/base, commands/results, fixtures/toolchain/config/dependencies, relevant file/transitive dependency/contract fingerprints or explicit impact rationale. Link historical evidence; never claim old run executed on new SHA. Unknown/changed inputs invalidate evidence; rerun affected and all project-mandated exact-head checks. Check current CI, rules and permissions. No blanket stale evidence or approval reuse.
- Focused recheck is intermediate, not a separate GitHub approval or new lifecycle label. If blockers remain, return one REQUEST_CHANGES (or appropriate blocked verdict) and convergence decision. If the initial independent review already covers the whole current candidate and has no blockers, it is the final review; do not start another pass. After remediation, perform **final independent whole-candidate review on exact current head and base** in same invocation where possible: reconcile all acceptance, full diff/affected paths, current mandatory checks/evidence, dispositions, reuse rationale and risk; inspect new/uncovered/invalidated areas. Avoid repeating unchanged specialist work merely for ritual. Required high-risk checks, stricter consumer reviews and formal non-author approval remain mandatory. Only final review may APPROVE with zero unresolved material blockers, valid authority and no missing mandatory evidence. Head/base movement invalidates approval; reassess and obtain new exact-head approval.
- Output/persist stage (initial/focused/final), cycle count, open/resolved IDs, progress, impact/coverage, evidence reuse rationale and escalation status in authorized issue/PR or host state before handoff. Apply same rules to consumer preflight, then formal review remains separate. New stage does not grant another automatic three-cycle budget.

## Fast, safe recovery

At restart: look up exact issue/PR and head, ownership/claim, stage, last approved snapshot, open review threads and required CI. Resume **the last valid checkpoint**; do not re-ask already valid approvals. If head changed, reverify affected tests and review under the convergence policy; if acceptance changed, revisit plan Gate 1. Restore the same ledger and cumulative count; do not restart the budget.

A workflow blocked on access or tools must state precisely what action was and was not performed. Do not label a planned action as a completed side effect.
