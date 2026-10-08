---
name: create-issue
description: Convert an idea or incomplete issue into a small testable GitHub work item by asking one material question at a time; not for implementation, planning bureaucracy or inventing decisions.
---

# Create issue

## Invocation contract
`/create-issue <idea-or-Issue>`. New idea or existing issue number; repository must be resolved from active project. Do not guess a specific issue.

## When to use
Use when creating or refining work that cannot yet pass the shared 12-point Definition of Ready (DoR).

## Do not use
Do not create duplicates, silently broaden milestone scope, force 3–5 criteria when a single clear criterion suffices, or ask every DoR item as a separate ritual question.

## Required context
Read only relevant requirements, design decisions (`## Design nuance`), code/expected behavior, dependencies, existing issues/PRs and `docs/WORKING-LOOP.md`.

## Stop or escalate when
Desired outcome conflicts with accepted authority, a material decision needs an owner, a duplicate already represents the outcome, or the issue is too broad to be independently verified.

## Procedure
1. Search duplicate issues/PRs and existing decisions **before** questions. If an existing issue covers the request, offer refinement rather than creating another.
2. Extract the problem, observable current vs expected behavior (including failure case), scope/non-goals, dependencies, security impacts and acceptance checks from existing context. Propose a best-practice solution, clearly distinguishing recommendation from accepted decision.
3. **Ask exactly one high-impact unanswered question per turn**; give a suggested answer and brief tradeoff. Never ask what authoritative sources already answer. If all decisions are known, ask zero questions.
4. Keep one coherent independently reviewable outcome. Add a short 3–7-step permanent-production implementation plan and criterion→test/evidence map inside the issue; no parallel planning artifact unless project policy requires it.
5. Evaluate all 12 DoR entries; missing optional verification *command* is not a blocker if the evidence strategy is clear. Record accepted design under `## Design nuance`; unresolved `!+concern` affecting scope/behavior blocks readiness.
6. Show an editable issue preview including title, current/expected, in/out, AC, plan, dependencies, risks/controls and compact readiness matrix; ask to create/update it **once**. Do not perform tracker writes until approval.
7. On approval, search duplicates and recheck governance once more; create/update issue, apply `needs:implementation` only if fully ready, and return actual URL. If blocked, save as refinement only with user approval.

## Output contract
Issue draft or URL, issue/source revisions, DoR verdict and gap rows, implementation steps, AC→test evidence, design decisions, single next question if any, explicit write approval/state and next skill.

## Handoff
READY → `implement-issue <N>`; unresolved authority → named decision owner. Do not claim the item automatically.
