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
Start with the user's problem. Load only relevant requirements, decisions (`## Design nuance`), code/expected behavior, dependencies and candidate/duplicate search. Read `docs/WORKING-LOOP.md#task-first-execution-and-progressive-context` and applicable readiness/authority sections; no full framework or project dump.

Treat an ADR merged into the authoritative branch as accepted without a separate status or approval step. Verify the source revision; do not treat unmerged ADR text as authority, and do not invent choices deferred by a merged ADR. See `docs/WORKING-LOOP.md`.

## Stop or escalate when
Desired outcome conflicts with accepted authority, a material decision needs an owner, a duplicate already represents the outcome, or the issue is too broad to be independently verified.

## Procedure
1. Search duplicate issues/PRs and existing decisions **before** questions. If an existing issue covers the request, offer refinement rather than creating another.
2. Extract the problem, observable current vs expected behavior (including failure case), scope/non-goals, dependencies, security impacts and acceptance checks from existing context. Propose a best-practice solution, clearly distinguishing recommendation from accepted decision.
3. **Ask exactly one high-impact unanswered question per turn**; give a suggested answer and brief tradeoff. Never ask what authoritative sources already answer. If all decisions are known, ask zero questions.
4. Keep one coherent independently reviewable outcome. Choose the risk lane and add only the necessary production plan and criterion→evidence map. LIGHTWEIGHT can be one obvious action or 1–3 steps; no separate planning artifact unless required.
5. Assess applicable DoR entries; report only material exceptions for LIGHTWEIGHT, missing optional verification *command* is not a blocker if the evidence strategy is clear. Record accepted design under `## Design nuance`; unresolved `!+concern` affecting scope/behavior blocks readiness.
6. Show an editable issue preview with title, expected outcome, scope, observable acceptance and applicable plan/risks/dependencies; for LIGHTWEIGHT keep it short and omit the routine matrix; ask to create/update it **once**. Do not perform tracker writes until approval.
7. On approval, search duplicates and recheck governance once more; create/update issue, apply `needs:implementation` only if fully ready, and return actual URL. If blocked, save as refinement only with user approval.

## Output contract
Issue draft or URL, relevant source revisions, readiness verdict/material gaps, proportional plan/evidence, decisions only if needed, write approval/state and next action.

## Handoff
READY → `implement-issue <N>`; unresolved authority → named decision owner. Do not claim the item automatically.
