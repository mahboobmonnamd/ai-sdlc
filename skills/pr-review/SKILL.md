---
name: pr-review
description: Orchestrate an independent merge-readiness review of an exact pull-request or equivalent merge-candidate revision across code review, verification, authority, scope, evidence, risk, checks, measurements, and residual risk.
---

# PR review

## When to use

Use after implementation has produced a merge candidate and before merge/release handoff when the question is: “Is this exact revision genuinely ready to merge?”

This is the user-facing final PR review capability. The caller should not need to separately invoke `code-review`, `verification`, or every specialist review first. This skill orchestrates or consumes those capabilities as required by project policy, risk, and evidence freshness, then synthesizes one merge-readiness verdict.

Use `code-review` directly instead when the narrower question is only whether an implementation/diff contains defects or regressions and no merge-readiness decision is requested.

Use the same procedure for a pull request, merge request, change list, patch stack, or other merge candidate. Do not require a particular host or VCS.

## Do not use

- Do not infer acceptance from green checks, reviewer confidence, work-item checkboxes, or a persuasive change description.
- Do not treat implementation plausibility as proof that mandatory acceptance criteria are satisfied.
- Do not reuse measurements, reviews, or checks from a different revision unless governing policy explicitly permits that evidence to carry forward.
- Do not silently reinterpret a benchmark, test, demo, or environment limitation to make an acceptance criterion pass.
- Do not require every possible specialist review for every change; derive rigor from project rules and material risk.
- Do not merge, approve, or mutate the change unless the task explicitly grants that authority. The default action is a review verdict and handoff.
- Do not make new product, architecture, security, compliance, performance-budget, or scope decisions during review.
- Do not duplicate specialist procedures inside this skill when an applicable reusable review capability exists; orchestrate and synthesize them.

## Required context

Load the smallest authoritative set that can establish:

- the merge candidate identity, base, exact current revision, and changed scope;
- the owning work item and its acceptance/definition-of-done rules;
- governing requirements, specifications, decisions, and project review rules;
- the actual diff/change set plus surrounding production code needed to trace affected paths;
- relevant tests, fixtures, failure coverage, build/check results, and workflow/check status;
- claimed performance/resource measurements and their methodology where applicable;
- security/privacy/accessibility/operability evidence where applicable;
- documentation, change description, release notes, or other claims that will become historical record;
- prior `code-review`, `verification`, and specialist-review outputs when they exist.

Treat previous verdicts as evidence inputs, not authority. Reconstruct the required outcome from authoritative sources before accepting implementation rationale.

Where the host exposes immutable revision identifiers, record the exact reviewed revision before analysis and resolve it again before the final verdict.

## Stop or escalate when

Return a blocking or inconclusive verdict when:

- the owning work item, accepted requirements, or authority hierarchy is missing, contradictory, or stale;
- the merge candidate revision changes and the unreviewed delta could affect the verdict;
- implementation contradicts approved architecture, scope, trust boundaries, or ownership;
- mandatory acceptance criteria lack reproducible evidence;
- checks/tests passed only on an older revision and no policy permits that evidence to carry forward;
- tests were weakened, skipped, narrowed, mocked around the production path, or otherwise fail to prove the claimed outcome;
- a benchmark label does not match its actual start/stop boundary, mixes rejected/deferred work into successful samples without disclosure, or otherwise overstates what was measured;
- a required measurement was attempted in an incapable environment and no valid alternate evidence exists;
- documentation/change-description claims exceed what the implementation and evidence establish;
- material security, privacy, compliance, accessibility, performance, concurrency, lifecycle, migration, compatibility, or operability risk lacks the specialist review required by project rules;
- the change contains unrelated high-risk work, temporary production paths, duplicate authorities, or unclassified exploratory code;
- the reviewer cannot inspect enough of the production path to distinguish real behavior from a test-only or mock path.

Do not convert an environmental limitation into a false pass. Classify it explicitly and determine whether the mandatory criterion is satisfied by alternate evidence, remains inconclusive, or is waived by an existing authoritative rule.

## Procedure

1. **Freeze review identity.** Record the candidate identifier, base, exact revision, mergeability/state when available, changed-file/change-set size, and any relevant dependency revision. Do not rely on a human-written “final revision” if the host exposes the actual current revision.

2. **Reconstruct authority.** Read the owning work item, acceptance criteria, definition of done, governing requirements/decisions, and project-specific review rules. Build the acceptance matrix before reading implementation claims. Separate:
   - what the product/system must do;
   - what architecture/security/performance constraints forbid or require;
   - what evidence is required to prove completion.

3. **Confirm scope.** Compare the actual change set with explicit in-scope and out-of-scope boundaries. Flag unrelated cleanup, hidden migrations, dependency changes, generated artifacts, temporary paths, or future-scope implementation that changes review risk.

4. **Run or consume `code-review`.** For non-trivial production changes, ensure an independent `code-review` covers the exact applicable revision and relevant surrounding code. If an existing code-review result is current and adequate, consume it; otherwise invoke/rerun it. Treat code-review approval as evidence for implementation quality, not as merge readiness. Independently follow up any acceptance-critical or high-risk path whose correctness is not fully established by the focused review.

5. **Run or consume `verification`.** Map every mandatory acceptance criterion to reproducible evidence. If current verification exists for the applicable revision and scope, consume it; otherwise invoke/rerun `verification`. Classify each mandatory row as:
   - `PROVEN` — reproducible evidence directly supports the criterion on the applicable revision/environment;
   - `FAILED` — evidence demonstrates the criterion is not met;
   - `INCONCLUSIVE` — evidence is absent, stale, indirect, contradictory, or insufficient;
   - `ENVIRONMENT_UNSUPPORTED` — the attempted environment cannot exercise the required capability. This is not a pass by itself.

6. **Audit tests and checks.** Verify relevant tests/checks actually ran against the reviewed revision and represent the claimed behavior. Inspect important tests instead of treating names/counts as proof. Look for weakened assertions, ignored/skipped coverage, mock-only validation, stale caches/artifacts, or workflow conditions that bypass the important path.

7. **Audit measurements.** For every material performance/resource claim, identify:
   - exact timer/counter start;
   - exact stop;
   - workload and state sampled;
   - warm-up/steady-state treatment where relevant;
   - sample count/statistical method where relevant;
   - build/configuration/environment;
   - exact revision;
   - whether instrumentation changes the measured path;
   - whether the printed label truthfully describes the boundary.
   Reject or downgrade mislabeled, contaminated, stale, inherited-without-authority, or non-reproducible measurements.

8. **Review environment-limited evidence.** If a required capability cannot run in the default automation environment, require explicit classification plus project-authorized alternate evidence, such as a controlled physical-device, hardware, privileged, networked, or interactive-environment run. Confirm that the environmental limitation does not hide unrelated failures.

9. **Run or consume specialist reviews by risk.** Apply project-required specialist review only where material. At minimum consider security/privacy, performance/resources, concurrency/lifecycle, data migration/integrity, accessibility, reliability/operability, public API/protocol compatibility, and supply chain. Reuse a current specialist result when it covers the exact applicable revision and risk; otherwise invoke/rerun the specialist capability. Missing required specialist review is blocking; irrelevant specialist ceremony is not.

10. **Review claims and historical record.** Compare the change description, work-item state, documentation, release notes, benchmark tables, and comments with the actual reviewed revision. Stale revision IDs, old numbers, unsupported completion claims, or misleading scope statements must not survive final acceptance.

11. **Adversarially search for unrepresented states.** Green automation proves only represented behavior. Identify important state combinations, race/failure modes, rollback/recovery paths, partial-write/partial-commit behavior, repeated persistent failures, and lifecycle transitions appropriate to the risk. Either show they are tested, prove them impossible by construction, or classify the residual risk.

12. **Re-check the exact revision.** Immediately before final verdict, resolve the merge candidate again. If the revision changed, determine whether the delta is trivially metadata-only under project policy or invalidate affected review/evidence and inspect the new delta. Never state “ready to merge” for an unreviewed revision.

13. **Synthesize, do not average.** A single unresolved mandatory blocker keeps the verdict from passing even if every other category is strong. Distinguish implementation defects from evidence/metadata gaps so remediation is narrow and honest.

## Output contract

Return a compact but auditable result with this structure:

```text
verdict: READY_TO_MERGE | CONDITIONAL | CHANGES_REQUIRED | BLOCKED_BY_DECISION | INCONCLUSIVE
reviewed_revision: immutable revision identifier when available
base_revision_or_target: identifier when available

blocking_findings:
  - severity
  - subsystem/file/path when available
  - violated requirement or acceptance criterion
  - concrete failure/evidence gap
  - narrow remediation direction

non_blocking_findings:
  - correctness/maintainability/performance/security/evidence/documentation improvements

acceptance_matrix:
  authority_and_scope
  architecture_and_ownership
  code_review
  production_correctness
  failure_concurrency_lifecycle
  verification_and_acceptance_evidence
  tests_and_checks
  security_privacy_compliance_if_applicable
  performance_resources_if_applicable
  accessibility_operability_if_applicable
  exact_revision_evidence
  documentation_claim_accuracy
  residual_risk

evidence_matrix:
  criterion -> PROVEN | FAILED | INCONCLUSIVE | ENVIRONMENT_UNSUPPORTED -> evidence reference

measurement_table_if_applicable:
  metric/requirement
  target
  measured statistics
  environment/configuration
  revision
  methodology assessment
  PASS | FAIL | INCONCLUSIVE

residual_risks:
  only risks that remain after applying project acceptance policy

merge_recommendation:
  YES | NO | ONLY_AFTER_LISTED_CONDITIONS
```

Verdict semantics:

- `READY_TO_MERGE` — no blocking finding remains; every mandatory criterion is proven or explicitly handled by existing project policy; exact-revision checks/evidence are sufficient.
- `CONDITIONAL` — implementation is acceptable but only narrowly defined non-code evidence/metadata/administrative conditions remain and project policy permits merge after those conditions are satisfied without code changes.
- `CHANGES_REQUIRED` — code/tests/configuration/evidence-generation logic must change before merge.
- `BLOCKED_BY_DECISION` — authority/specification/product/security/compliance decision is unresolved and cannot be invented during review.
- `INCONCLUSIVE` — required evidence/access/environment is insufficient to determine readiness honestly.

Never report `READY_TO_MERGE` when a mandatory evidence row is `FAILED` or `INCONCLUSIVE`. `ENVIRONMENT_UNSUPPORTED` may coexist with readiness only when authoritative policy defines valid alternate evidence and that alternate evidence is `PROVEN` for the reviewed revision.

## Handoff

- `READY_TO_MERGE` → merge/release authority may proceed under project policy; this skill does not perform the merge by default.
- `CONDITIONAL` → satisfy the listed non-code conditions, re-check the exact revision and affected evidence, then hand off to merge/release authority.
- Implementation/test/measurement-instrumentation defect → `implementation`, then rerun affected `code-review`, specialist review, `verification`, and this `pr-review` as required by risk.
- Missing/weak acceptance evidence without implementation defect → `verification`, then rerun this `pr-review`.
- Scope/authority conflict → `work-item-design` or the project decision workflow, then `development-readiness` before implementation resumes.
- Specialist gap → required specialist review, then rerun affected acceptance rows and this `pr-review`.
- Revision changed → review the new delta and rerun invalidated checks/evidence before issuing another merge-readiness verdict.
