# AI-SDLC canonical working loop

Normative operating rules for all active skills. Design rationale and performance goals: [SDLC-DESIGN.md](SDLC-DESIGN.md).

## 12-point Definition of Ready

Display each PASS / FAIL / UNKNOWN / N/A with a one-line reason/evidence, grouping satisfied rows when screen space matters. Only item 5 (the command) is optional. Material FAIL or UNKNOWN is blocking.

| # | Check | PASS means |
| --- | --- | --- |
| 1 | Problem stated | Outcome, user/affected system and why |
| 2 | Observable behavior | Concrete current vs expected behavior and material negative cases |
| 3 | Bounded scope | In scope/out of scope; independently reviewable |
| 4 | Verifiable acceptance | Testable, externally observable pass/fail criteria |
| 5 | Verification command (optional) | Useful known command specified; if absent, expected evidence still named |
| 6 | Design decisions closed | Decisions under `## Design nuance`; relevant open `!+concern` explicitly block |
| 7 | Congruence | Compatible with accepted product intent, architecture and code ownership |
| 8 | Dependencies | Named, correctly ordered, satisfied or explicitly gated |
| 9 | Not duplicate | Search issues, open PRs, merged changes and candidate branches |
| 10 | Self-contained | Issue + resolvable authoritative links suffice without private conversation |
| 11 | Implementation plan | 3–7 ordered production steps with criterion-to-test map |
| 12 | Security controls | Trust boundaries, access, secrets, inputs, privacy and failure risks assessed; N/A justified |

DoR is an **outcome contract**, not an excuse for bureaucratic prose. A sufficient issue is its own plan. An external versioned plan is required only if project policy explicitly demands it. Load its exact accepted revision; a merely proposed plan cannot authorize changes. A coordination-only label or timestamp edit does not invalidate accepted scope; changed behavior, dependencies or decisions do.

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

## Four user decisions, no ritual approvals

| Moment | Display | Ask |
| --- | --- | --- |
| New/refined issue | Final issue body + DoR evidence | Approve creation/update? |
| Implement Gate 1 | DoR readiness, exact issue revision, short plan, testing/risk strategy | **Proceed with implementation? (yes/no)** |
| Implement Gate 2 | diffstat, exact branch/base/head, acceptance-to-evidence matrix, self-review, complete PR title/body | **Push branch and create PR? (yes/no)** |
| Process-review | All actionable findings+CI, dispositions, file/test impact, unresolved authority | **Apply this plan? (yes/no)** |

The approval applies to a **specific snapshot**. If materially changed requirements, plan or reviewed diff invalidate an approval, show only the material delta and seek an updated decision (not a blanket repeat). A no means no corresponding action; do not pretend work happened. Explicit `/pr-merge <PR>` already authorizes a merge attempt, subject to mandatory checks.

## Verification and merge

- Every mandatory acceptance criterion must show exact test/measurement/demonstration, observed result and revision. Evidence `PASS/FAIL/INCONCLUSIVE`; unrun is not PASS.
- Use narrow tests during coding and broader risk-driven evidence before Gate 2: normal path, negative/errors, auth/security, compatibility, concurrency/lifecycle, storage/migration/recovery, performance/operability only where relevant.
- Verify final local diff has no hidden debug changes, unrelated scope, test weakening, secret exposure, temporary production substitute or unchecked migration.
- After push, CI and GitHub review status are **fresh again**. Pushing and opening a PR is not merge readiness. Review against exact current PR head + base; stale approval is not valid. Respect code owners, required checks, merge queue, blocking threads, rulesets and current permission. No branch-protection bypass.
- `[CRIT]`, `[SEC]` and `[NONCONF]` block approval when materially unresolved. `[IMPR]` is non-blocking; `[GOOD]` is positive evidence. Findings need file/line when applicable, failure mechanism and an actionable correction.
- `process-review` handles review stage only; classify every finding as should fix / improvement / discard / disagree / push back. A justified disagreement can clear an invalid blocker only through a new independent reviewer decision; the implementer cannot approve their own resolution.

## Fast, safe recovery

At restart: look up exact issue/PR and head, ownership/claim, stage, last approved snapshot, open review threads and required CI. Resume **the last valid checkpoint**; do not re-ask already valid approvals. If head changed, reverify affected tests and review; if acceptance changed, revisit plan Gate 1.

A workflow blocked on access or tools must state precisely what action was and was not performed. Do not label a planned action as a completed side effect.
