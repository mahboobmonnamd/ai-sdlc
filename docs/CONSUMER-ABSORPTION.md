# Consumer absorption map

Generic AI-SDLC skills own reusable workflow semantics. Consuming projects keep tracker identity, branch/worktree mechanics, product/domain gates, and posting/mutation policy.

This change intentionally removes the overlapping generic code-review entrypoint and introduces explicit planning and review-remediation stages.

## Pin sequence

~~~text
ai-sdlc workflow change
  → review/merge in ai-sdlc
  → consumer updates exact framework pin
  → consumer facades map tracker-native identifiers to generic arguments
  → consumer adds only project-specific governance deltas
~~~

Do not copy the generic procedure into always-on agent rules or create parallel consumer skills that compete for the same intent.

## Core generic → consumer mapping

| Generic capability | Consumer facade responsibility |
| --- | --- |
| project-context(query) | Map project indexes/sources; keep authoritative-source precedence |
| work-item-design(work_item_id/outcome) | Map tracker issue/ticket semantics and project issue protocol |
| implementation-planning(work_item_id) | Persist/reference durable plan identity/revision and add project-specific file/module/test/build constraints without changing accepted authority |
| development-readiness(work_item_id) | Apply project Ready rules; persist gap report only under explicit user authorization |
| implementation(work_item_id) | Map tracker-native ID, claim semantics, deterministic branch/worktree, open-merge-candidate detection, and post-implementation merge-candidate creation/resolution |
| verification(work_item_id, revision) | Add project-specific evidence/gates |
| pr-review(merge_candidate_id) | Add project architecture/hot-path/specialist requirements; this is the only review entrypoint |
| address-pr-review(merge_candidate_id) | Map review threads/checks and candidate update authority; batch all known remediation |

## Required consumer behavior for issue-based implementation facades

When a project exposes an issue-number command such as implement-issue:

1. require the issue number as the explicit argument;
2. fetch the issue fresh;
3. if another developer already owns/claims it, stop before branch/worktree/files/edits;
4. require a current accepted implementation plan with durable `plan_id` + `plan_revision`;
5. resolve open PR/merge-candidate state: if none, start new implementation; if the same authorized candidate exists and implementation is incomplete, resume implementation on that same candidate; if another/ambiguous owner or multiple active candidates exist, stop and reconcile;
6. if an open PR exists and the user is addressing reviewer feedback/check failures, route to address-pr-review rather than implementation;
7. after completed implementation with no candidate, create or resolve the concrete PR/merge candidate under consumer policy before invoking pr-review;
8. if readiness fails, show the generic gap table and prepare the project-specific gap report artifact;
9. do not post tracker comments without explicit user confirmation.

A consumer may choose a deterministic local filename for the preview artifact. That filename convention belongs to the consumer, not the generic framework.

## Review semantics

A consumer must not reintroduce code-review as a competing generic facade. pr-review already owns implementation correctness, architecture/scope review, evidence/CI, specialist risk, and final merge readiness.

Every re-review remains full-candidate. address-pr-review owns remediation only and always returns to full pr-review.

## Do not absorb into generic skills

Keep these consumer-owned:

- tracker identity/assignee/claim mechanics;
- branch/worktree naming;
- PR templates and exact tracker comment APIs;
- product/domain architecture;
- platform-specific test commands;
- specialist domain skills;
- merge permissions and human approval policy.

Reusable workflow defects should be fixed in AI-SDLC rather than copied into project-specific facades.
