---
name: work-item-design
description: Turn an accepted outcome into one independently reviewable work item; not for implementation planning, ownership claiming, or inventing unresolved product/architecture decisions.
---

# Work item design

## Invocation contract

Use one of:

```text
work_item_id: authoritative existing work-item identifier to refine
```

or, when creating a new work item:

```text
outcome: accepted product/system outcome to decompose into a work item
```

Do not guess an existing tracker identifier. If neither an existing work item nor an accepted outcome can be established, stop.

## When to use

Use when requirements/decisions are understood but the executable unit of work is vague, oversized, under-specified, or unsafe to hand to planning/implementation.

## Do not use

- Do not invent missing product behavior or architecture decisions.
- Do not collapse a broad milestone into one oversized item merely to avoid decomposition.
- Do not prescribe tracker, branch, or repository mechanics unless the consuming project requires them.
- Do not mix unrelated cleanup with the requested outcome.
- Do not ritualize clarifying questions when the outcome is already specified.
- Do not use vague acceptance such as “production-ready”, “professional”, or “looks good”.
- Do not claim or assign implementation ownership; that belongs to the consuming project's implementation governance.

## Required context

Load:

- accepted outcome/requirement and measurable success behavior;
- governing decisions/specifications and constraints;
- dependency/current-work state;
- relevant component/ownership boundaries;
- known risks and rigor profile;
- verification expectations.

If upstream authority itself is uncertain, stop and route to the corresponding requirements/decision activity. Final `development-readiness` runs only after this work item and its implementation plan exist.

## Stop or escalate when

Stop and route elsewhere when:

- product behavior/acceptance intent is unresolved;
- architecture/ownership/trust-boundary decisions are missing;
- feasibility materially needs a spike;
- authoritative sources conflict/stale;
- the item cannot be independently verified without bundling unrelated work.

## Procedure

1. Resolve the existing `work_item_id` or accepted `outcome`.
2. Define one coherent outcome that can be reviewed and verified independently; prefer a thin vertical path from input to observable result.
3. Ask clarifying questions only for material unresolved choices, using the fewest questions that change the design.
4. Link exact authoritative requirements/decisions/specifications. If a source cannot be established, write `unknown`.
5. Define explicit in-scope and out-of-scope boundaries.
6. Identify dependencies, blockers, owning component/boundary, and sequencing constraints.
7. Write 3–5 measurable acceptance criteria in observable terms.
8. Define evidence required to prove completion: tests, fixtures, integrations, measurements, demos, specialist review, or other checks as applicable.
9. Classify security/privacy/performance/accessibility/documentation/operability impacts.
10. Check parallelizability. If multiple items touch the same authority or unstable seam, encode the dependency/order.
11. Right-size the work. Split independently reviewable slices into child/sub-items. A parent planning item must not implicitly lock all children; the consuming project's ownership policy decides claim scope, and independently implementable children should remain independently claimable unless authority says otherwise.
12. If the requested outcome cannot finish in one implementation unit, name what to split/drop. Cut scope, not acceptance.
13. End with a readiness-for-planning statement. Do not call the item implementation-ready while authority, acceptance, dependency, or feasibility blockers remain.

## Output contract

Return:

```text
work_item_id_or_new_item
outcome
why
source_authority
in_scope
out_of_scope
dependencies_and_blockers
ownership_boundary
acceptance_criteria: 3-5 checkable conditions
required_evidence
slice_plan_or_child_items
risk_and_specialist_impacts
verification_procedure
readiness_for_planning: READY | REFINEMENT_REQUIRED | BLOCKED
next_action: implementation-planning | decision-activity | spike | split
ownership_claim: NOT_PERFORMED
blocking_reason
unknowns
```

## Handoff

- READY → `implementation-planning`, then project-defined plan acceptance, then `development-readiness`.
- Missing authority/acceptance → appropriate upstream decision/requirements activity, then re-run work-item design.
- Material feasibility unknown → isolated non-mergeable spike.
- Oversized work → recursively design smaller dependent work items.
- A proposed plan is not readiness. After plan acceptance records `accepted_plan`, run `development-readiness` before `implementation`.
