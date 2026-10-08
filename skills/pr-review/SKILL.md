---
name: pr-review
description: Independently review an exact PR head against intended behavior, affected production paths and required evidence, posting structured inline GitHub feedback; not for implementation edits or merge.
---

# PR review

## Invocation contract
`/pr-review <PR>` with exact PR number. Works for both AI-SDLC issues and PRs without an owning issue.

## When to use
Initial review and full re-review after remediation or head/base changes.

## Do not use
Do not review only new lines or latest comments, claim green CI equals correctness, approve own authored PR via an unsupported self-review, edit code, or merge.

## Required context
Fresh PR head/base/current diff (all pages and changed files), issue scope/AC and plan when applicable, design authority, relevant surrounding code/call paths, security controls, required CI/evidence, prior reviews and unresolved threads. For a standalone PR, reconstruct intent from PR/repository authority without inventing an issue.

## Stop or escalate when
Merged/closed/rejected candidate, already-merged-equivalent content, ambiguous base, incomplete diff access, unauthorized review claim, head changes during review, or missing mandatory evidence. Use INCONCLUSIVE, never a false APPROVE.

## Procedure
1. **Fast eligibility:** inspect candidate lifecycle and ownership; distinguish incomplete feature work (`IMPLEMENTATION_IN_PROGRESS` → `implement-issue`) from review-ready work. Check already-merged changes, stale base, duplicate PR and conflicts. State exactly what is stale and whether rebase is actually required.
2. Atomically claim PR review in shared `pr:<N>` exclusion domain; recheck claim owner/token, then transition `needs:review` → `pr:reviewing`. Do not change state on a failed claim.
3. Freeze head SHA/base. Inventory **all** changes, surrounding contracts and affected usage, relevant tests and previous findings; do not rely on patch alone for correctness. Determine risk coverage: behavior, errors/failure, security/privacy, authorization, data/concurrency, compatibility, migration/rollback, performance/operability where relevant, documentation and CI.
4. Review independently and **finish the full material finding pass**, even after first blocker. Categorize: `[CRIT]` correctness/reliability defect; `[SEC]` security/privacy control; `[NONCONF]` accepted intent/contract deviation or mandatory missing evidence; `[IMPR]` optional quality; `[GOOD]` proven strength. Group siblings by root cause; include how failure manifests, expected outcome, exact source link/line and smallest valid remediation.
5. Correlate original acceptance→evidence, tests and CI to the **current SHA**. Do not treat tests/skips from an older head as success. Prior findings are a regression checklist, not a substitute for reviewing whole candidate. Review code while CI runs where useful, but final approval needs required checks/evidence.
6. Re-fetch head and check state before posting. Changed head → do not post a stale verdict. Post **one structured GitHub review**: summary, blockers, non-blocking improvements, positive notes, AC/CI matrix and actionable inline comments on changed lines. If inline position is impossible, use a precise file/line summary rather than fabricating coordinates.
7. Final verdict: REQUEST_CHANGES if any unresolved CRIT/SEC/NONCONF or mandated evidence gap; APPROVE only for clean intent-matching, verified **independent** review (IMPR-only may APPROVE); INCONCLUSIVE when review inputs/tools are inadequate. If self-approval is prohibited, post COMMENT and return "independent approval required", not a simulated approval.
8. Release owned claim safely. On valid requested changes set `needs:processing`; on valid approval for exact head set `needs:merge`; otherwise return to `needs:review` with blocker. Remove `pr:reviewing` only after successful reconciled transition.

## Output contract
PR/head/base, review coverage, exact evidence revision, old-finding dispositions, CRIT/SEC/NONCONF/IMPR/GOOD table and inline links, submitted review ID/URL, APPROVE/REQUEST_CHANGES/INCONCLUSIVE, label outcome, next action.

## Handoff
REQUEST_CHANGES → `process-review`; APPROVE → `pr-merge`; incomplete scope → `implement-issue`. Review revised head again in full.
