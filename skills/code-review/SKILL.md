---
name: code-review
description: Independently review an implemented change against approved scope, authority, correctness evidence, risks, and unintended effects without confusing plausibility with verification.
---

# Code review

## When to use

Use after implementation has produced a reviewable change set and before final verification/release readiness. Use it to assess whether the change is technically acceptable, scoped correctly, and supported by appropriate evidence.

## Do not use

- Do not act as final product verification merely because the code looks correct.
- Do not approve architecture-by-precedent when accepted decisions say otherwise.
- Do not rewrite the implementation wholesale unless the review task explicitly includes remediation.
- Do not require every specialist review for every change; use the risk/impact classification.
- Do not assume a specific pull-request host, VCS, language, or CI system.

## Required context

Load:

- the approved work item and acceptance criteria;
- governing requirements/decisions/specifications;
- the implementation diff/change set and affected tests;
- claimed validation/performance/security/documentation evidence;
- project-specific review rules and rigor profile.

Use `project-context` to minimize broad repository reading, then inspect authoritative sources and changed code directly.

## Stop or escalate when

Return a blocking review finding when:

- implementation exceeds or contradicts approved scope;
- an architecture/product/security/privacy/compliance decision was made silently in code;
- tests were weakened, bypassed, or rewritten around a defect;
- required evidence is absent or claims exceed measurements;
- unrelated high-risk changes are mixed into the change set;
- authoritative context is stale/conflicting;
- the reviewer lacks required specialist authority for a material risk.

## Procedure

1. Reconstruct the intended outcome from the work item and authoritative sources before reading implementation rationale.
2. Compare the actual change set against in-scope and out-of-scope boundaries.
3. Check ownership, dependency, API/data/trust boundaries, and other architectural constraints for silent drift.
4. Review correctness and failure behavior in the changed code, including edge cases appropriate to the risk profile.
5. Inspect tests/evidence for whether they prove intended behavior rather than merely mirror implementation details.
6. Look for weakened assertions, removed coverage, skipped checks, fake fixtures, or acceptance criteria translated into something easier.
7. Evaluate dependency/configuration/build changes and generated artifacts for hidden scope or supply-chain impact.
8. Validate performance/security/privacy/accessibility/operability/documentation claims only when applicable; request specialist review when risk warrants it.
9. Check that reproducible verification steps exist and that known limitations/deferred work are stated accurately.
10. Produce findings ordered by severity and concrete impact. Avoid style-only noise unless project conventions make it material.
11. Approve/recommend acceptance only when no blocking findings remain and required evidence is complete for review scope.

## Output contract

Return:

```text
verdict: APPROVE_FOR_VERIFICATION | CHANGES_REQUIRED | BLOCKED_BY_DECISION | SPECIALIST_REVIEW_REQUIRED
blocking_findings: concrete defects/violations with evidence
non_blocking_findings: useful improvements that do not block outcome
scope_assessment
architecture_authority_assessment
test_evidence_assessment
risk_specialist_assessment
verification_handoff
```

Approval means the implementation is suitable to proceed to `verification`; it does not prove the requested outcome is complete.

## Handoff

- Clean review → `verification`.
- Code defect/evidence weakness → `implementation` for remediation, then review again.
- Scope/authority problem → `work-item-design` or decision workflow, then `development-readiness`.
- Specialist risk → the appropriate specialist review before final verification.
