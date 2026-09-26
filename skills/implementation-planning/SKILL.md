---
name: implementation-planning
description: Produce or refresh the durable implementation plan for one accepted work item before readiness; not for coding, claiming ownership, accepting the plan, or deciding unresolved product/architecture questions.
---

# Implementation planning

## Invocation contract

Required argument:

```text
work_item_id: authoritative work-item identifier
```

The work item must already have accepted scope and acceptance criteria. This skill plans implementation; it does not claim the work item, create a branch, edit production code, or accept the plan.

## When to use

Use after `work-item-design` and before final `development-readiness` for every implementation work item. The rigor profile controls plan depth: lightweight work may use a compact plan, but the plan is never omitted.

## Do not use

- Do not invent product behavior, architecture, trust boundaries, or public contracts.
- Do not claim ownership or begin implementation.
- Do not accept the plan or advance `accepted_plan` on the work item/registry.
- Do not hide unresolved design forks inside an apparently concrete plan.
- Do not make a disposable POC the production plan.
- Do not overwrite a current accepted plan without preserving identity/provenance.

## Required context

Load the work item/acceptance criteria, governing requirements/decisions/specifications and their revisions, owning component/boundary, relevant current code/tests, dependencies, required evidence/risk classifications, and project engineering constraints.

## Stop or escalate when

Stop when scope/acceptance is unresolved, a required authority decision is missing, feasibility needs a spike, dependencies are unavailable, authoritative sources conflict, or the only apparent route contradicts accepted architecture.

## Procedure

1. Resolve and freshly read `work_item_id`.
2. Reconstruct accepted outcome/scope/acceptance and record the revisions of governing requirements/decisions/specifications.
3. Inspect only the current code/tests needed to understand the production path and integration boundaries.
4. Identify intended production surfaces and state/contract owners.
5. Define implementation sequence and dependency order.
6. Map acceptance criteria to planned tests/evidence and relevant failure paths.
7. Record migration/compatibility/rollback/recovery concerns where applicable.
8. Record risk/specialist/documentation gates that actually apply.
9. Surface unresolved material forks rather than choosing silently.
10. Ensure the plan uses the permanent intended architecture and introduces no disposable second path or duplicate authority.
11. Produce a durable plan identity. When creating a plan, allocate/return `plan_id`; when refreshing one, preserve `plan_id` and advance `plan_revision`. Persist the new revision as status `proposed`. The persistence layer must be able to resolve that exact revision to immutable plan content/provenance; latest-only mutable storage is insufficient.
12. **Do not** update the work item's/project registry's `accepted_plan` pointer. Plan creation and plan acceptance are separate. Only the project-defined technical-authority acceptance operation may set `accepted_plan` (with `accepted_by` / `accepted_at` or equivalent evidence).
13. Record `governing_revisions` for **planning-relevant semantic content** sufficient to decide later whether the plan is still current. Tracker coordination metadata such as claim/assignee/status/comment changes must not stale the plan unless they alter accepted scope, acceptance, dependencies, authority, or another planning input.
14. Produce a concise executable plan another competent implementer can follow without hidden reasoning.

## Output contract

```text
work_item_id
plan_id
plan_revision
proposed_plan_reference: <plan_id>@<plan_revision>
plan_content_ref: immutable/revision-addressable source for this exact plan revision
plan_status: PROPOSED | BLOCKED
accepted_plan_pointer: UNCHANGED
next_action: plan-acceptance | work-item-design | decision-activity | spike | BLOCKED
governing_revisions
production_surfaces
implementation_sequence
acceptance_to_test_evidence_map
dependencies
failure_paths
migration_compatibility_recovery_if_applicable
risk_and_specialist_gates
documentation_impact
assumptions
unknowns
blocking_decisions
```

A proposed plan is an input to acceptance and then `development-readiness`. It is not approval to code and must not be treated as the accepted-plan reference.

## Handoff

- PROPOSED → project-defined technical-authority **plan acceptance** (records `accepted_by` / `accepted_at` and advances `accepted_plan`), then `development-readiness`.
- Scope/acceptance defect → `work-item-design`.
- Product/architecture/other authority gap → explicit decision activity, then refresh the plan.
- Material feasibility unknown → isolated non-mergeable spike, then refresh the plan.
