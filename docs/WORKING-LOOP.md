# Working loop

Task-selected execution discipline for the existing development-loop skills. This is **not** a skill, **not** an always-on agent constitution, and **not** a replacement for product/architecture authority.

Agents must not paste this file into project `AGENTS.md`, always-apply rules, or a parallel skill that claims the same work as `work-item-design`, `implementation`, `code-review`, `verification`, or `pr-review`. Load only the row that matches the current activity. Multiple coding agents (Cursor, Claude, Codex, Copilot, and others) discover the same portable `skills/*/SKILL.md` files; keep this vendor-agnostic.

## Why this exists

A useful working loop tells an agent *when* to clarify, how thin a slice may be, what proof looks like, and what “done” means. Dumping those prompts into every session pollutes routing: clarifying questions fire on mechanical fixes, review-only hostility fires during implementation, and “tests only after it broke” fights evidence-first production work.

The existing catalog already owns most of this. This document records what was absorbed, what was rewritten, and what was rejected, so later consumer pins do not re-add the discarded wording.

## Selector

| Current activity | Skill | Load |
| --- | --- | --- |
| Ambiguous request, missing acceptance, oversized ticket | `work-item-design` then `development-readiness` | Before |
| Ready implementation | `implementation` | Before (skip-gated) + During |
| Focused diff/defect review | `code-review` | During (smallest-change) + After |
| “Is the outcome actually true?” | `verification` | After |
| “Is this exact revision mergeable?” | `pr-review` | After |
| Compact source retrieval | `project-context` | Any phase, sources only |

If the user names a skill, use that skill. Do not run the Before, During, and After columns as one checklist.

## Before — design and readiness

Use in `work-item-design` and `development-readiness`. Implementation may use a subset only when the task is still under-specified.

### Clarify only when it changes the result

If the request, work item, and authority already specify the outcome, **ask nothing**. If a material choice remains, ask the fewest questions that would change the work (typically 1–5), each with concrete options, then wait. Do not ritualize five questions.

Existing catalog already said: don’t invent product/architecture decisions; ask before assuming scope. The new rule only adds skip conditions and optioned questions.

### One vertical slice

A work item is one narrow path from input to an observable result, not a horizontal layer (schema now, API later, UI later).

- If a parent item contains multiple independently reviewable slices, recommend child/sub-items, one per slice. Keep a parent as the ownership/claim surface when the consuming project uses exclusive active-work claims.
- If the user asks for the full end-to-end outcome in this session, still design the slices, but do **not** require a pause after slice one before designing or implementing slice two.
- If the user asks to see slice N before slice N+1, stop after the named slice with something they can run.

Existing catalog already forbade mega-items and required independently reviewable outcomes. This adds parent/sub-item guidance and the e2e vs pause distinction.

### Working software on the permanent path

Every implementation pass must end with an exercisable path for this slice: a command, test, API, UI, or other observable behavior a human can run. Rough is allowed. Fake data, disposable prototypes, or a second production path are not allowed on a mergeable branch.

Existing production-vs-POC guardrail stays stricter and wins.

### Simplest thing that works

Build only what the current slice needs. Do not extract an abstraction for a second use; duplicate until a third independent copy. **Exception:** do not duplicate authoritative state, ownership, or a second engine/path. That exception already exists and is stronger than YAGNI.

### Cut scope, not time

If the requested outcome cannot finish in one implementation session, name what to drop or split. Do not keep the parent ambition and stretch. `READY` applies to the named slice, not the unscoped remainder.

## During — execute the slice

Use in `implementation`. `code-review` uses only the smallest-change and unknown/source rules.

### Proof, not a completion claim

Do not say the work is done. Show the check: command or test name, and a quoted exact line of output or source. Estimates stay labeled estimates.

### Change only the approved surface

Make the smallest possible change. Do not rewrite, reformat, or improve anything outside the work item. Existing “touch only what you must” stays; this makes unrelated cleanup an explicit defect.

### Compare three approaches only for material forks

When a real design fork exists, compare at least three approaches, mark uncertainty as `unknown`, pick one, and say why. Skip this for mechanical, specified, or single-obvious-path changes. Unresolved architecture is still a readiness/decision route, not an implementation vote.

### Write `unknown` instead of inventing a source

If a path, ID, measurement, or citation is not established, write `unknown`. Never invent a source. Existing authority rules already forbade silent invention; this makes the token explicit.

### Flag expensive-to-reverse decisions

Call out public contracts, data formats, authority splits, and hard dependencies before coding them. Existing architecture-escalation remains the stop condition; this is the warning label on the path that *is* allowed.

### Mark shortcuts

If a shortcut is taken (skipped generalization, duplicated logic, narrowed demo), record `shortcut:` in the handoff. Shortcuts are not secret architecture.

## After — review and prove

Use in `code-review`, `verification`, and `pr-review`. Do not run this hostility during implementation unless the user asked for review.

### Be blunt; do not improve

Find weaknesses. Rank them by severity. Do not soften. Do not “fix up” the change in a review-only pass. For a non-trivial change, surface the worst issues (up to 10). For a tiny mechanical diff, do not invent a top-10 list.

### Tests are for this slice, failures, and marked-critical behavior

**Rejected as written:** “tests only for what already broke” / “don’t write a test suite.”

That wording would weaken evidence-first core behavior and let untested acceptance ship. The absorbed rule is:

- Keep or add tests that prove this slice’s acceptance criteria.
- Add a regression for anything that has failed once.
- Add coverage the user marked critical.
- Do not add an opportunistic suite for unrelated code “while here.”
- Do not weaken existing tests.

### Definition of done is checkable

Done is 3–5 concrete observable conditions from the work item. Never “professional,” “production-ready,” or “looks good.” Verification maps those conditions to quoted evidence.

## What was not absorbed

| Requested prompt | Why it stays out of always-on / generic production |
| --- | --- |
| Always ask 5 questions before doing anything | Pollutes mechanical work; skip-gated clarification is enough |
| Pause after every slice even when the user asked for e2e | Conflicts with finishing the requested outcome |
| Duplicate freely with no exception | Would create split-brain state/engines; existing production-path rule wins |
| Tests only after a failure | Conflicts with evidence-first acceptance; rewritten above |
| Always dump a top-10 failure list | Noise on tiny diffs; review-only and severity-ranked |
| New always-apply Cursor rules | Vendor-specific and duplicates portable skills |

## Rigor

Lightweight profiles may skip unused specialist ceremony. They may not skip: specified-or-ask clarification, one coherent slice, quoted proof for claimed completion, `unknown` instead of invented sources, or checkable Done. High-rigor consuming projects may require more tests and reviews than this loop; they must not require less evidence than the skill they invoked.
