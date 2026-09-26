# Working loop

Task-selected execution discipline for the core development-loop skills. This is **not** an always-on agent constitution and does not replace product/architecture authority.

## Canonical workflow

~~~text
work-item-design <work-item|outcome>
        ↓
implementation-planning <work-item>
        ↓
development-readiness <work-item>
        ↓ READY
implementation <work-item>
        ↓
host/project creates or resolves merge candidate
        ↓
pr-review <merge-candidate>
        ├─ READY_TO_MERGE → merge/release authority
        └─ CHANGES_REQUIRED
                  ↓
         address-pr-review <merge-candidate>
                  ↓
              pr-review          ← always full candidate review
~~~

verification is an independently reusable evidence skill and is also consumed/orchestrated by pr-review. A standalone VERIFIED result never bypasses a PR-review gate required by project or rigor policy. project-context is a retrieval utility used by any stage.

There is intentionally **no standalone generic code-review skill**. A request to review a PR/merge candidate routes to pr-review, which owns implementation correctness plus merge-readiness evidence. A request to fix existing review comments routes to address-pr-review.

## Skill selector and invocation

| User intent | Skill | Required input | Key governance |
| --- | --- | --- | --- |
| Retrieve project authority/context | project-context | query | Summaries are navigation, not authority |
| Refine/create executable work item | work-item-design | work_item_id or accepted outcome | No implementation ownership claim |
| Produce implementation plan | implementation-planning | work_item_id | No code edits; no hidden authority decisions |
| Decide whether implementation may start | development-readiness | work_item_id | Non-ready must expose explicit gaps/cures/concerns |
| Implement new work | implementation | work_item_id | Ready + plan + no conflicting owner + no open merge candidate |
| Prove acceptance outcome | verification | work_item_id (+ revision when applicable) | Evidence per criterion; assertion is not evidence |
| Review/re-review merge candidate | pr-review | merge_candidate_id | Full review every time; all material blockers in one pass |
| Fix review comments/check failures | address-pr-review | merge_candidate_id | Inventory all unresolved feedback/checks, batch remediation |

If the user names a skill, use that skill unless doing so would violate its explicit stop condition.

## Readiness and implementation governance

Implementation is allowed only after all four are established. This order is canonical across rigor profiles; lightweight work may use a compact plan, but the plan still exists before readiness:

1. the exact work item is identified and current;
2. no other implementer owns/claims it under project policy;
3. an accepted implementation plan exists;
4. no conflicting merge candidate already owns this implementation lifecycle. An authorized existing candidate for the same unfinished work item is a continuation surface, not a blocker.

After implementation, merge-candidate creation/resolution is host/project integration, not hidden work inside `implementation`. If the same authorized merge candidate already exists and implementation is incomplete, continue `implementation` on that candidate. If its purpose is reviewer-feedback/check remediation, route to `address-pr-review`. `pr-review` starts only once implementation is complete and a concrete candidate identifier exists.

When readiness fails, development-readiness returns a table with:

| Gap | What's missing | Proposed cure (when inferable) | Concerns / decision needed |
| --- | --- | --- | --- |

It also produces tracker-comment-ready full text. The consuming tracker facade decides file naming/posting mechanics and must obtain explicit user authorization before posting.

### Existing merge-candidate routing

```text
open candidate for same work item?
  ├─ no → implementation may create work; host/project later creates/resolves candidate
  ├─ yes + authorized owner + implementation incomplete → continue implementation on SAME candidate
  ├─ yes + review comments/check remediation → address-pr-review
  └─ yes + other/ambiguous owner or multiple candidates → BLOCK and reconcile
```

Never create a second candidate merely because implementation spans sessions.

## Implementation discipline

Build only the accepted slice and permanent production path. Do not silently change architecture, weaken acceptance, create temporary parallel implementations, or perform unrelated cleanup.

When a material design fork appears that accepted authority does not resolve, stop and route backward. A plan is not permission to invent an architecture decision.

For claimed progress, show reproducible proof: exact command/check plus a quoted result or source. Write unknown when evidence cannot be established.

## PR review discipline

Every pr-review is a **full review of the entire current candidate**, including re-review after remediation.

The review must cover implementation correctness, scope/architecture, affected production paths, tests, failure/lifecycle/concurrency behavior, acceptance evidence, required CI, measurements, specialist risk where applicable, and documentation/claim accuracy.

Continue after finding blockers. Complete the review coverage and return every material blocker discovered in the pass. Group duplicate symptoms by root cause; do not hide independent findings and do not apply an arbitrary finding cap.

## Review remediation discipline

address-pr-review is the only core review-remediation entrypoint.

Before editing it inventories:

- all unresolved review threads/comments;
- all prior material review findings;
- all required failing checks/CI.

It then fixes the complete known material set as one bounded batch, searches the approved surface for sibling instances of each root cause, reruns relevant checks, and hands the exact new candidate back to pr-review.

Do not fix one comment and immediately request re-review while other known blockers remain.

## Re-review semantics

Prior findings are a regression checklist, not the review boundary. The latest delta is context, not scope.

Expensive checks or measurements may be reused only when governing policy proves they remain valid for the current revision. Every acceptance row and risk domain is still reconsidered.

The convergence target is one complete finding pass plus one full re-review after batched remediation when feasible. There is no hard round cap that can hide correctness or evidence problems.

## Checkable Done

Done comes from concrete observable work-item acceptance conditions. Never substitute “production-ready”, “looks good”, green CI alone, or reviewer confidence for acceptance evidence.
