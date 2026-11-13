---
name: pr-review
description: Independently review an exact PR head against intended behavior, affected production paths and required evidence, posting structured inline GitHub feedback; not for implementation edits or merge.
---

# PR review

## Invocation contract
`/pr-review <PR>` with exact PR number. Works for both AI-SDLC issues and PRs without an owning issue.

## When to use
Initial full review, focused remediation recheck and final whole-candidate exact-head review under `docs/WORKING-LOOP.md#review-convergence-and-evidence-reuse`.

## Do not use
Do not issue delta-only approval, review only new lines or latest comments for a final verdict, claim green CI equals correctness, approve own authored PR via an unsupported self-review, edit code, or merge.

## Required context
Fresh PR head/base/current diff (all pages and changed files), issue scope/AC and plan when applicable, design authority, relevant surrounding code/call paths, security controls, required CI/evidence, prior reviews and unresolved threads. For a standalone PR, reconstruct intent from PR/repository authority without inventing an issue.


## ADR review

Apply `docs/WORKING-LOOP.md#adr-lifecycle-merge-is-acceptance`. An ADR on the authoritative branch is accepted regardless of legacy status text; verify its actual merged content. An ADR-bearing PR is proposed until merge, but a final coherent decision (and any included implementation/tests) is eligible for APPROVE if the normal independent review and evidence gates pass. Do not return CONDITIONAL solely because that PR's own ADR is not yet merged; authorized merge is the acceptance event. An unresolved choice, unmerged external ADR prerequisite or other material authority gap remains a blocker. Review approval is not acceptance before merge.

## Provisional contract review

When the consumer explicitly permits provisional implementation, review the whole candidate now against the accepted baseline and the issue's exact provisional ledger. Assess containment, disabled/fail-closed behavior, reversibility, tests, and whether any unresolved choice has leaked into authorization, privacy, persistence, protocol, or user-visible claims. Continue technical findings while independent authority review is pending.

If the candidate safely satisfies its provisional contract but an external authority decision is pending, return `CONDITIONAL` with the exact acceptance-before-merge dependency. A final ADR in the same PR is reviewed under ADR review above. Do not require that decision before technical review, and do not turn technical APPROVE/CONDITIONAL into pre-merge ADR/spec acceptance. Any unsafe or uncontained uncertainty remains a blocking finding.

## Stop or escalate when
Merged/closed/rejected candidate, already-merged-equivalent content, ambiguous base, incomplete diff access, unauthorized review claim, head changes during review, or missing mandatory evidence. Use INCONCLUSIVE, never a false APPROVE.

## Procedure
1. **Fast eligibility:** inspect candidate lifecycle and ownership; distinguish incomplete feature work (`IMPLEMENTATION_IN_PROGRESS` → `implement-issue`) from review-ready work. Check already-merged changes, stale base, duplicate PR and conflicts. State exactly what is stale and whether rebase is actually required.
2. **Executable claim:** atomically acquire a PR ownership token; use `PHASE=review`, `NUMBER=<PR number>` and run `python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" begin --repo "$REPO" --phase review --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"` with the common host-configured DB and worker identity (`docs/WORKING-LOOP.md`). `ACQUIRED` or `RESUMED` must be followed by a `verify` call returning `VERIFIED` before `needs:review` → `pr:reviewing` or any review/label mutation. The same PR claim resource excludes `process-review` simultaneously. On `BUSY`/`DENIED`/`ERROR` do not write, review or spawn a duplicate candidate; explain the existing owner/configuration.
3. Freeze head SHA/base. Inventory **all** changes, surrounding contracts and affected usage, relevant tests and previous findings; do not rely on patch alone for correctness. Restore the shared convergence ledger; classify initial/focused/final, inspect complete candidate diff inventory and impacted dependencies, verify previous evidence provenance and exact applicability. Focus interim recheck on fixes and affected paths; expand immediately when impact is unknown or high risk per canonical policy. Determine risk coverage: behavior, errors/failure, security/privacy, authorization, data/concurrency, compatibility, migration/rollback, performance/operability where relevant, documentation and CI.
4. Review independently and **finish the full material finding pass**, even after first blocker. Categorize: `[CRIT]` correctness/reliability defect; `[SEC]` security/privacy control; `[NONCONF]` accepted intent/contract deviation or mandatory missing evidence; `[IMPR]` optional quality; `[GOOD]` proven strength. Group siblings by root cause; include how failure manifests, expected outcome, exact source link/line and smallest valid remediation.
5. Correlate original acceptance→evidence, tests and CI to the **current SHA**. Do not treat tests/skips from an older head as success. Prior findings are a regression checklist. Reuse only proven unchanged historical observations/evidence with independent equivalence and linked provenance; rerun affected and all mandatory exact-head checks. Focused recheck cannot approve. When blockers close, perform final independent whole-candidate exact-head review in the same invocation where possible; reconcile all criteria, paths, dispositions, current checks and reused evidence. Review code while CI runs where useful, but final approval needs required checks/evidence.
6. Re-fetch head and check state before posting. Changed head → do not post a stale verdict. Post **one structured GitHub review**: summary, blockers, non-blocking improvements, positive notes, AC/CI matrix and actionable inline comments on changed lines. If inline position is impossible, use a precise file/line summary rather than fabricating coordinates.
7. Convergence and final verdict: update durable cycle count, open/resolved finding IDs and progress; after 3 routine remediation cycles with blockers or earlier no-progress trigger, stop automatic remediation and escalate with canonical packet. Do not request another automatic batch. Only final independent whole-candidate exact-head review may APPROVE.  REQUEST_CHANGES if any unresolved CRIT/SEC/NONCONF or mandated evidence gap; CONDITIONAL when the candidate safely satisfies a documented provisional contract but external authority acceptance remains pending; APPROVE only when the candidate is merge-ready and clean intent-matching, verified **independent** review (IMPR-only may APPROVE); INCONCLUSIVE when review inputs/tools are inadequate. CONDITIONAL never sets the candidate to merge-ready. If self-approval is prohibited, post COMMENT and return "independent approval required", not a simulated approval.
8. Re-verify the claim before review submission and label changes, then perform the reconciled transition: valid requested changes → `needs:processing`; exact-head approval → `needs:merge`; `CONDITIONAL` → retained authority blocker and no `needs:merge`; otherwise return to `needs:review` with blocker. Remove `pr:reviewing` only after the transition succeeds. Then invoke `python3 "$AI_SDLC_TOOL_ROOT/tools/workflow_claims.py" release --repo "$REPO" --phase review --number "$NUMBER" --token-file "$AI_SDLC_CLAIM_TOKEN_FILE"`. Retain the same token/claim across interrupted review until a valid handoff or authorized cancellation.

## Output contract
PR/head/base, review coverage, exact evidence revision, old-finding dispositions, CRIT/SEC/NONCONF/IMPR/GOOD table and inline links, submitted review ID/URL, APPROVE/CONDITIONAL/REQUEST_CHANGES/INCONCLUSIVE, label outcome, review stage, cycle count, stable finding IDs, impact/evidence reuse rationale, escalation status and next action.

## Handoff
REQUEST_CHANGES → `process-review`; APPROVE → `pr-merge`; CONDITIONAL → decision owner resolves the listed authority gate, then revalidate the same candidate; incomplete scope → `implement-issue`. Revised head → focused recheck if safe, full review for unknown/high-risk impact, final whole-candidate exact-head review before approval. Escalated → named owner, no automatic recursive handoff.
