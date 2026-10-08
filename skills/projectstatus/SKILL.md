---
name: projectstatus
description: Reconcile milestone implementation plan with current GitHub issues/PRs into an evidence-backed HTML dashboard; not for mutating progress or inventing completion.
---

# Project status

## Invocation contract
`/projectstatus [milestone]` with optional approved plan file/URL or current repo plan discovery.

## When to use
To see milestone delivery reality, scope drift, review/CI bottlenecks and next unblockers.

## Do not use
Do not fabricate plan, delivery dates, issue counts or velocity, equate closed issue with acceptance, or silently exclude unplanned tickets.

## Required context
Authoritative plan source and revision if available; all paginated milestone issues, PRs/merge status/CI, milestone ownership/dependencies and snapshot time.

## Stop or escalate when
Plan missing/stale, incomplete access/pagination or ambiguous milestone. Produce an INCOMPLETE dashboard with explicit source/data gaps, never a falsely green one.

## Procedure
1. Fetch all scoped issues/PRs and authoritative implementation plan revision. Reconcile IDs with plan work items; show planned-untracked and unplanned-tracked separately, and deduplicate parent/child progress.
2. Compute READY/IMPLEMENTING/REVIEW/PROCESSING/MERGE_READY/BLOCKED/NEEDS_REFINEMENT/DONE/UNKNOWN with verified evidence, not label guess alone. Document unknown denominators and unmatched items.
3. Surface milestone health: completion coverage, critical dependency blockers, stale updates, CI failures, review queue aging, scope change and due-date risk **only when dates exist**.
4. Normalize data to `references/SNAPSHOT.md`; run `scripts/render_dashboard.py --data <snapshot.json> --output <dashboard.html> [--milestone <name>]`. Verify file exists and visually/readably contains plan and tracker source links. Escaped, self-contained responsive HTML; no external scripts or secrets.
5. Return actual HTML artifact plus short textual snapshot, top blockers and three evidence-based actions. Do not mark the report GENERATED if only instructions were produced.

## Output contract
Artifact link/path, snapshot date, selected milestone and plan revision, completeness, reconciled/missing/unplanned counts, status/risk evidence, bottlenecks, unknowns and next three actions.

## Handoff
READY → `describe-backlog` / `whats-next-for-me`; missing authority → `create-issue`; no state mutation.
