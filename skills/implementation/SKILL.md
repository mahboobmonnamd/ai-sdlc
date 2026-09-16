---
name: implementation
description: Execute one ready work item within its approved scope using evidence-first development, explicit authority boundaries, continuous validation, and a reviewable handoff.
---

# Implementation

## When to use

Use when a work item has passed `development-readiness`, its scope and acceptance behavior are explicit, and implementation is the correct next activity.

## Do not use

- Do not use implementation to resolve missing product or architecture decisions.
- Do not silently broaden scope, perform unrelated cleanup, or introduce speculative abstractions.
- Do not weaken valid tests or acceptance criteria to fit the implementation.
- Do not claim completion merely because code compiles, a happy path works, or local tests pass.
- Do not assume a specific language, framework, tracker, branch model, or build command unless the consuming project defines it.
- Do not place spike/prototype/POC code on a mergeable production path. Exploratory code belongs on an explicitly isolated, non-mergeable branch/worktree or equivalent environment.
- Do not add a temporary parallel implementation, alternate engine/view/renderer, or duplicate state path to production merely because the permanent implementation is not ready.

## Required context

Load only what is needed for the ready work item:

- work-item outcome, in/out scope, dependencies, and acceptance criteria;
- governing requirements/decisions/specifications;
- owning component and relevant code/tests;
- required verification and specialist-impact classifications;
- current rigor profile and project-specific engineering instructions;
- the consuming project's active-work ownership/claim policy, when one exists.

Use `project-context` for compact retrieval, then read consequential authoritative sources.

## Exclusive work-item claim

When the consuming project defines an exclusive ownership or active-work claim mechanism, acquiring and verifying that claim is a mandatory implementation preflight.

1. Read the work item from the authoritative tracker immediately before implementation begins; do not rely on stale chat, cached project context, or a previous read for ownership state.
2. If another implementer already owns or has claimed the work item, do not create a worktree, branch, files, or production edits. Stop with `BLOCKED` and report the current owner/claimant when the tracker exposes it.
3. If the work item is unclaimed, acquire the project-defined claim using its authoritative mechanism before implementation work starts.
4. Re-read the authoritative work item after the write and verify that the claim belongs to the current implementer. Treat an ambiguous, multiple-owner, overwritten, failed, or unverifiable claim as a collision and stop.
5. If the consuming project defines an additional collision backstop such as a deterministic issue branch, lease, lock, or status transition, satisfy and verify it before creating the implementation worktree or editing production files.
6. Never steal, replace, clear, or bypass another implementer's valid claim merely to continue. Ownership transfer requires the consuming project's explicit handoff/reassignment procedure.
7. A claim is coordination metadata, not proof of readiness, correctness, or completion. All normal readiness, architecture, testing, review, and verification gates still apply.

If the consuming project has no exclusive claim policy, continue without inventing tracker-specific ownership semantics.

## Stop or escalate when

Stop implementation and route appropriately when:

- another implementer already owns the work item or the active-work claim cannot be acquired and verified;
- evidence contradicts an accepted requirement, specification, or architecture decision;
- a new product/architecture/security/privacy/compliance decision is required;
- scope expansion is necessary to succeed;
- a dependency is missing or has changed incompatibly;
- a material technical unknown requires a spike;
- the only available route is a disposable/temporary implementation that would create a second production path;
- acceptance criteria are discovered to be untestable or contradictory;
- authoritative context is stale or conflicting.

Do not create precedent by coding through these conditions.

## Procedure

1. Reconfirm the ready work item, its authority, exact scope, and **production intent** before changing production behavior. If the work is exploratory, stop and route it to an isolated spike/POC instead of treating it as implementation.
2. Apply the consuming project's exclusive work-item claim policy when one exists. Do not create the implementation worktree/branch or edit production files until the claim is acquired and verified for the current implementer.
3. Identify the smallest test, fixture, executable check, or other observable evidence that can fail before the intended behavior exists. For core behavior, prefer test/evidence-first development when feasible.
4. Implement the smallest coherent **production** change that satisfies the accepted outcome without speculative future architecture. An MVP may intentionally be narrow or incomplete in feature breadth, but every merged code path must belong to the intended permanent architecture.
5. Never promote exploratory code merely because a spike succeeded. Preserve useful findings as measurements, docs, decision evidence, fixtures, or independently valid tests; then implement the production solution cleanly under normal readiness/quality rules.
6. Run the narrowest relevant checks continuously while developing.
7. Preserve unrelated behavior. If unrelated defects or cleanup are discovered, record them separately unless they block this work.
8. Re-check assumptions whenever implementation reveals new evidence. Route authority-changing discoveries instead of deciding silently.
9. Exercise failure paths and boundaries appropriate to the risk profile, not only the happy path.
10. Run the project's required formatting/static/unit/integration/security/performance/documentation checks that apply to this work item.
11. Compare any claimed measurements against reproducible baselines. Label estimates as estimates and do not convert a smoke result into a product claim.
12. Assess documentation/operational impact before handoff. User-visible or contributor-visible changes should update the appropriate documentation when the project requires it.
13. Prepare a reviewable change set with traceability from work item → implementation → tests/evidence. Do not self-certify final outcome verification.

## Output contract

Return or record:

```text
implemented_scope
active_work_claim: NOT_APPLICABLE | VERIFIED_CURRENT_IMPLEMENTER | BLOCKED_BY_OTHER | CLAIM_FAILED
active_work_owner_or_claimant
changed_surfaces
tests_or_evidence_added
checks_run_and_results
known_limitations_or_deferred_work
new_risks_or_decisions_discovered
documentation_or_specialist_impact
review_handoff
status: IMPLEMENTED_FOR_REVIEW | BLOCKED | RETURN_TO_DECISION | NEEDS_SPIKE
```

`IMPLEMENTED_FOR_REVIEW` means implementation work is ready for independent review/verification; it is not a final correctness verdict.

## Handoff

- Normal path → `code-review`, then `verification`.
- Active-work collision → remain `BLOCKED` until the consuming project's explicit ownership handoff/reassignment procedure makes the work item available.
- Authority conflict → corresponding decision/artifact skill, then re-run `development-readiness`.
- Material technical uncertainty → isolated, non-mergeable `technical-spike`; after evidence/decision, start a clean production implementation path.
- Scope change → `work-item-design` before continuing.
