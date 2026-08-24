---
name: work-item-design
description: Turn an accepted outcome into one implementation-ready, independently reviewable work item with explicit scope, dependencies, acceptance criteria, risks, and verification evidence.
---

# Work item design

## When to use

Use when requirements, decisions, or a milestone are sufficiently understood but the executable unit of work is vague, oversized, under-specified, or unsafe to hand to an implementation agent.

## Do not use

- Do not invent missing product behavior or architectural decisions.
- Do not turn a broad milestone into one oversized implementation item merely to avoid decomposition.
- Do not prescribe a tracker, branch naming convention, repository workflow, or technology unless the consuming project already requires it.
- Do not mix unrelated cleanup with the requested outcome.

## Required context

Load:

- accepted outcome/requirement and measurable success behavior;
- governing decisions/specifications and known constraints;
- dependency and current-work state;
- relevant component/ownership boundaries;
- known risks and applicable rigor profile;
- verification expectations.

Use `development-readiness` when it is unclear whether upstream authority is sufficient.

## Stop or escalate when

Stop work-item design and route elsewhere when:

- product behavior or acceptance intent is unresolved;
- architecture/ownership/trust-boundary decisions are missing;
- feasibility is materially unknown and needs a spike;
- authoritative sources conflict or are stale;
- the proposed item cannot be independently verified without bundling unrelated work.

## Procedure

1. Define one coherent outcome that can be reviewed and verified independently.
2. State why the work exists and which accepted outcome it advances.
3. Link or identify exact authoritative requirements/decisions/specifications rather than paraphrasing them into a competing source of truth.
4. Define explicit in-scope behavior and explicit out-of-scope boundaries.
5. Identify dependencies, blockers, owning component/boundary, and any sequencing constraints.
6. Write measurable acceptance criteria in terms of observable outcomes, not implementation activity.
7. Define the evidence required to prove completion: tests, fixtures, integration checks, measurements, demos, specialist review, or other verification as applicable.
8. Classify security/privacy/performance/accessibility/documentation/operability impacts and route specialist work only when relevant.
9. Check parallelizability. If multiple items would mutate the same authoritative state or unstable boundary, make the dependency/order explicit instead of assuming concurrency is safe.
10. Right-size the item. Split when outcomes, authorities, or verification methods are independently reviewable; keep together when splitting would create artificial partial states.
11. End with a readiness statement. Do not label the item implementation-ready while a blocking decision or evidence gap remains.

## Output contract

Return a work-item definition containing at minimum:

```text
outcome
why
source_authority
in_scope
out_of_scope
dependencies_and_blockers
ownership_boundary
acceptance_criteria
required_evidence
risk_and_specialist_impacts
verification_procedure
readiness: READY | REFINEMENT_REQUIRED | BLOCKED
blocking_reason (when not READY)
```

## Handoff

- READY → `implementation-planning`/`test-design`/`implementation` according to project workflow.
- Missing authority or acceptance → `development-readiness` and the appropriate upstream artifact/decision skill.
- Material feasibility unknown → `technical-spike`.
- Oversized work → recursively design smaller dependent work items before implementation.
