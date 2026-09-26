---
name: development-readiness
description: Decide whether one planned work item may begin implementation and report blocking gaps; not for designing the work item, writing its plan, or coding through unresolved authority.
---

# Development readiness

## Invocation contract

Required input:

```text
work_item_id: authoritative work-item identifier
```

If no existing work item exists yet, use `work-item-design` first. If the caller cannot identify the target and context does not resolve exactly one item, ask for the identifier rather than guessing.

## When to use

Use before implementation begins, resumes after a material decision, or expands into materially different scope. Use it to answer whether the identified work item is implementation-ready and what concretely blocks it when it is not.

## Do not use

- Do not design the solution merely to make work appear ready.
- Do not replace product discovery, architecture design, technical specification, work-item design, or implementation planning.
- Do not treat existing code as authority when approved requirements/decisions say otherwise.
- Do not mark work ready because an agent is confident or implementation has already started.
- Do not mark mergeable production work ready while the intended code is still a spike/prototype/POC.
- Do not mark a parent ambition READY when only a thinner slice can finish; name the slice.
- Do not hide a non-ready verdict behind prose. Surface each material gap explicitly.

## Required context

Load the smallest authoritative set needed to judge the identified work item:

- intended outcome and acceptance behavior;
- applicable requirements, decisions, specifications, constraints, and risks;
- current work-item state and dependencies;
- accepted implementation-plan identity, revision, governing revisions, and current/stale status;
- known technical unknowns/spikes;
- applicable rigor profile;
- stale/conflicting context indicators.

Use `project-context` first when a compact index exists, then open the authoritative sources that materially affect the verdict.

## Stop or escalate when

Return a non-ready verdict rather than guessing for:

- product decision required;
- architecture/ownership/trust-boundary decision required;
- technical unknown requiring evidence from a spike/prototype/measurement;
- missing or materially incomplete implementation plan;
- acceptance gap that prevents objective verification;
- dependency blocker;
- stale/conflicting authority;
- required specialist/risk-owner decision.

## Procedure

1. Resolve and freshly read `work_item_id`.
2. Restate the requested outcome without adding implementation assumptions.
3. Identify authoritative requirements/decisions/specifications and current work-item/dependency state.
4. Check unresolved authority/product decisions before implementation details.
5. Check material technical uncertainty; route uncertainty to an isolated non-mergeable spike rather than burying it in production implementation.
6. Check that acceptance criteria are observable, testable, and sufficient to distinguish success from plausible partial implementation.
7. Check dependencies and predecessor work.
8. Check scope, ownership boundaries, and non-goals for uncontrolled expansion risk.
9. Resolve the work item's/project registry's **accepted-plan reference** first, then load the immutable content for that exact `plan_id + plan_revision`. If the exact revision cannot be resolved, treat the plan as missing/inconclusive rather than falling back to latest. Do not choose an arbitrary related/latest plan. Verify its planning-relevant `governing_revisions` still match current authoritative scope/acceptance/dependency/requirement/decision/specification content. Coordination-only tracker changes (claim/assignee/status/comments) do not stale the plan by themselves. Missing identity, missing accepted revision, or incompatible planning input makes the plan MISSING/STALE. Lightweight work may use a compact plan, but a hidden plan inside agent reasoning does not satisfy this gate.
10. Confirm production/default-branch work follows the intended permanent architecture and yields an observable/exercisable path.
11. Apply the project's rigor profile without skipping unresolved authority, acceptance, or material-risk gates.
12. Flag expensive-to-reverse decisions.
13. If the outcome cannot finish as one implementation unit, READY applies only to a named independently reviewable slice.
14. Produce exactly one verdict.

When the verdict is anything other than `READY`, also produce a gap table with **one row per material gap**:

| Gap | What's missing | Proposed cure (when inferable) | Concerns / decision needed |
| --- | --- | --- | --- |

Do not invent a cure when authority or evidence is insufficient; write `unknown` and identify who/what must decide.

Then generate a tracker-comment-ready `gap_report_body` containing the same findings and proposed next actions. The generic skill returns the body; the consuming tracker facade decides whether/how to persist it and must not post without explicit user authorization.

## Output contract

Return:

```text
work_item_id
verdict: READY | NOT_READY | AWAITING_DECISION | NEEDS_SPIKE | BLOCKED
reason
blocking_items
implementation_plan: PRESENT | MISSING | STALE | UNKNOWN
accepted_plan_reference: <plan_id>@<plan_revision> | MISSING | UNKNOWN
accepted_plan_id
accepted_plan_revision
next_capability
resume_condition
evidence_used
hard_to_reverse_decisions
named_slice_if_scope_cut
unknowns
gap_table: required when verdict != READY
gap_report_body: tracker-comment-ready full text when verdict != READY
```

A READY verdict means implementation may begin within the assessed scope; it does not mean implementation is complete or correct.

## Handoff

- READY with accepted plan → `implementation`.
- Missing/weak work-item scope or acceptance → `work-item-design`.
- Missing/stale implementation plan → `implementation-planning`, then re-run readiness.
- Technical uncertainty → isolated non-mergeable spike, then re-run readiness.
- Product/architecture/other authority gap → explicit decision/escalation workflow.
- Stale/conflicting context → reconcile authoritative sources before continuing.
- Non-ready tracker persistence → consumer facade may preview/post `gap_report_body` only after explicit user confirmation.
