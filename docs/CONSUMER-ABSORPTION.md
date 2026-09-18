# Consumer absorption map

How consuming projects should take the working-loop changes after this repository lands them. Generic skills remain the authority for reusable procedure. Consumers keep domain, tracker, and product gates.

This pass updates **AI-SDLC only**. Do not copy these paragraphs into a consumer `AGENTS.md`. After the next reviewed pin, fold only the consumer-specific rows.

## Pin sequence

```text
ai-sdlc working-loop change
  → review/merge in ai-sdlc
  → consuming OSS project updates the exact bootstrap pin
  → consumer facades stay thin; add a delta only when the generic rule is insufficient
  → commercial overlays inherit the OSS pin; they do not shadow generic skills
```

Do not edit a pinned `oss/` checkout from a commercial change. Do not create Cursor-only `.cursor/rules` copies of these procedures.

## Map: rewritten loop → generic skill → later consumer delta

| Loop rule | AI-SDLC skill (this change) | Later consumer absorption | Do not absorb |
| --- | --- | --- | --- |
| Clarify only when it changes the result | `work-item-design`, skip-gated in `implementation` | Issue-refinement / implementation facade: keep “ask before assuming”; add skip-if-specified if still missing | Always-on AGENTS.md “ask 5 questions” |
| Vertical slice + parent/sub-items | `work-item-design` | Issue-refinement: recommend child items per slice; parent may remain the exclusive-claim surface | Forcing a pause between slices when the user asked for e2e |
| Working software, permanent path | `implementation`, `development-readiness` | Implementation facade already forbids POC-on-production; keep that stricter rule | Fake UI/data to look finished |
| Duplicate until third copy, except authority splits | `implementation` | Keep consumer cohesion/hot-path rules; they already forbid duplicate state engines | Using YAGNI to justify a second VT/runtime/renderer |
| Cut scope, not time | `work-item-design`, `development-readiness`, `implementation` | Implementation plan-first: name dropped slice instead of stretching | Shrinking acceptance after seeing the code |
| Quoted proof | `implementation`, `verification`, `pr-review` | Verification adapter: require command/output quotes in handoff | Treating green CI as the quote |
| Smallest change only | `implementation`, `code-review` | Already present (“do not refactor unrelated”); keep | Drive-by formatting |
| Three approaches for material forks | `implementation` | Architecture-change already compares alternatives; do not duplicate that workflow into implementation PRs | Three approaches for mechanical fixes |
| Write `unknown` | `project-context`, all loop skills | Keep “don’t hide confusion”; add the token where facades still paraphrase | Invented citations |
| Expensive-to-reverse + shortcuts | `implementation`, `development-readiness` | Architecture-change for irreversible authority; implementation handoff for shortcuts | Silent shortcuts as architecture |
| Blunt ranked review, don’t improve | `code-review`, `pr-review` | PR-review facade: keep blocking findings; don’t add a mandatory top-10 on tiny diffs | Running review hostility during implementation |
| Slice/failure/critical tests only | `implementation`, `code-review` | Keep test-first for core/VT behavior; do not import “tests only after it broke” | Dropping fixture/conformance requirements |
| 3–5 checkable Done conditions | `work-item-design`, `verification` | Issue protocol acceptance checkboxes; never “production-ready” as Done | Vague professional language |

## Consumer skills that should stay domain-owned

These should **not** receive the generic working-loop text. They already have stronger or different jobs:

- architecture-change / ADR workflow
- domain TDD, conformance, fuzzing, renderer, performance, security
- native UI/accessibility/visual-regression
- documentation authoring/validation
- milestone aggregation
- tracker identity, assignee, branch, and PR templates

If a reusable defect is found while operating those skills, fix the generic catalog here rather than growing a second implementation/review skill in the consumer.

## Suggested follow-up work items (not this change)

1. Pin the merged AI-SDLC revision in the OSS consumer bootstrap.
2. Diff each facade against `docs/WORKING-LOOP.md`. Add only missing skip conditions; delete restated generic procedure.
3. Keep commercial overlays as a composition delta. Do not shadow `implementation`, `work-item-design`, `code-review`, `verification`, or `pr-review`.
