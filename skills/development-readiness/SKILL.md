---
name: development-readiness
description: Decide whether implementation may begin, or route unresolved product, architecture, evidence, dependency, or acceptance gaps to the correct SDLC activity.
---

# Development readiness

## When to use

Use before implementation begins, resumes after a material decision, or expands into a materially different scope. Use it when someone asks whether work is ready to build, whether an issue/task is implementation-ready, or what is blocking development.

## Do not use

- Do not design the solution merely to make work appear ready.
- Do not replace product discovery, architecture design, technical specification, work-item design, or verification.
- Do not treat existing code as authority when approved requirements or decisions say otherwise.
- Do not mark work ready because an agent is confident or because implementation has already started.

## Required context

Load only the smallest authoritative set needed to judge readiness:

- intended outcome and acceptance behavior;
- applicable requirements, decisions, specifications, constraints, and risks;
- current work item and dependency state;
- known technical unknowns/spikes;
- applicable rigor profile;
- stale/conflicting context indicators.

Use `project-context` first when a compact index is available, then open the authoritative sources that materially affect the verdict.

## Stop or escalate when

Return a non-ready verdict instead of guessing when any of these applies:

- **product decision required** — behavior, scope, priority, acceptance, or user outcome is unresolved;
- **architecture decision required** — ownership, system boundary, major dependency, trust boundary, public contract, or other architectural choice is unresolved;
- **technical unknown** — feasibility or a material mechanism needs evidence from a spike/prototype/measurement;
- **acceptance gap** — success cannot be objectively verified;
- **dependency blocker** — required upstream work or external capability is unavailable;
- **stale/conflicting authority** — sources disagree or derived context is stale;
- **risk owner required** — security, privacy, legal, safety, compliance, or other specialist authority must decide.

## Procedure

1. Restate the requested outcome without adding implementation assumptions.
2. Identify the authoritative artifacts and decisions that constrain it.
3. Check for unresolved decisions and authority gaps before implementation details.
4. Check material technical uncertainty. Route uncertainty to `technical-spike`; do not bury it inside production implementation.
5. Check that acceptance criteria are observable, testable, and sufficient to distinguish success from a plausible partial implementation.
6. Check dependencies and required predecessor artifacts/work.
7. Check that scope, ownership boundaries, and non-goals are explicit enough to prevent uncontrolled expansion.
8. Apply the project's rigor profile: lightweight work may need fewer artifacts, but it may not skip unresolved authority, acceptance, or material-risk gates.
9. Produce exactly one primary verdict and the smallest next action needed to advance.

## Output contract

Return:

```text
verdict: READY | NOT_READY | AWAITING_DECISION | NEEDS_SPIKE | BLOCKED
reason: concise evidence-backed explanation
blocking_items: IDs or concrete gaps
next_capability: the SDLC skill/activity that should run next
resume_condition: what must become true before readiness is re-evaluated
evidence_used: authoritative sources actually relied on
```

A READY verdict means implementation may begin within the assessed scope; it does not mean implementation is complete or correct.

## Handoff

- READY → `work-item-design` if the executable work item is still weak, otherwise `implementation-planning`/`test-design`/`implementation` as appropriate.
- Missing acceptance/scope → requirements or `work-item-design`.
- Technical uncertainty → `technical-spike`.
- Product/architecture/other authority gap → explicit decision/escalation workflow.
- Stale/conflicting context → reconcile authoritative sources before continuing.
