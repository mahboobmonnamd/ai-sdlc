---
name: projectstatus
description: Reconcile a project's implementation plan with current milestone issues and generate a self-contained HTML status dashboard; not for changing issue state.
---

# Project status

## Invocation contract
`/projectstatus [milestone]`; optional path or URL to authoritative implementation plan.

## When to use
Use to assess delivery progress, slippage, coverage, dependencies and milestone health.

## Do not use
Do not fabricate milestone scope, dates, estimates, velocity or completion; do not equate closed issues with accepted work.

## Required context
Fetch authoritative current implementation plan/revision, all GitHub issues and PRs for selected milestones (paginate), labels, dependencies, linked evidence, blockers and current date.

## Stop or escalate when
Plan is absent, ambiguous or stale: still produce the dashboard, prominently flag reconciliation INCOMPLETE and report unmatched plan items/unknowns. Never silently invent a plan.

## Procedure
1. Match plan work items to issue IDs and PRs; show unmatched plan rows and unplanned tracker work separately. Deduplicate parent/child progress.
2. Calculate counts from actual issues; categorize READY, IMPLEMENTING, REVIEW, PROCESSING, MERGE_READY, DONE, BLOCKED and UNMAPPED. Mark ambiguous states UNKNOWN.
3. Derive health signals: scope coverage, blockers, aging/stale issues (with actual update dates), failing checks, review/processing queues, dependency bottlenecks, due-date risk only when dates exist. State metric denominators.
4. Generate **one self-contained, accessible, responsive HTML** artifact with an executive summary, milestone filter/sections, progress and risk indicators, plan-versus-GitHub reconciliation table, status drill-down hyperlinks and a short recommended next-actions section.
5. Escape all issue/user-provided text; no remote scripts, tokens, secrets or misleading simulated data. Keep data timestamp and source links visible.
6. Provide the generated HTML file/link and a short textual snapshot; never say generated when no file was created.

## Output contract
Return actual HTML artifact, snapshot date, plan revision/source, milestone scope, matched/unmatched counts, issue-status and health summaries, top blockers, known data gaps and next three evidence-backed actions.

## Handoff
Ready work → `describe-backlog` / `whatsnextfor-me`; unclear issues → `create-issue`. No automatic mutations.
