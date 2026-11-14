# Consumer adoption

Adopt a reviewed AI-SDLC pin. Product architecture, requirements, test commands, issue/PR labels and GitHub credentials stay in the consuming repository; do not duplicate the full generic lifecycle in every project's always-on rules.

| Previous capability | New entrypoint |
| --- | --- |
| `work-item-design` | `create-issue` |
| `implementation-planning`, `development-readiness`, `implementation` | `implement-issue` (two gates, issue-owned plan) |
| `address-pr-review` | `process-review` (one batch gate) |
| `pr-review` | `pr-review` (independent, full diff and evidence) |
| Host merge operation | `pr-merge` with standard protections |
| Backlog planning | `describe-backlog` / `whats-next-for-me` |
| Delivery reconciliation | `projectstatus` HTML dashboard |

`project-context` and `verification` remain reusable support skills. Historical tools for plan acceptance and resumption can remain for older consumers but **must not create additional human approval gates** in the new workflow.

## Adopt without duplicating workflow

Consumers must reconcile legacy prompts, always-on rules, pinned skills and CI with the [task-first policy](WORKING-LOOP.md#task-first-execution-and-progressive-context). Keep only domain-specific deltas in adapters; route natural-language intent directly to the active skill. Use named section reads from the pinned `tools/read_policy.py` or equivalent range retrieval; do not inject the full canonical policy into every agent turn. Declare which checks are applicable by risk/path and which must run at exact head. Prefer deterministic CI for mechanical rules. Existing stricter requirements remain binding until explicitly changed by the consumer's authority. Do not silently weaken security, architectural, evidence, ownership or branch-protection gates.

Pilot the revised pin on representative lightweight documentation, normal feature/fix and critical changes. Record actual model input/output tokens (when exposed), context bytes, active/wait time, full/focused review passes, repeated root causes, CI executions and escaped defects; compare like-risk baseline PRs, with missing metrics reported as unknown. Run actual adapters/agents, not only static tests. Do not claim savings before measurement.

## Required adapter capabilities

1. Fresh, paginated issue/PR/CI/review/branch retrieval, exact head and dependency graph.
2. **Real atomic exclusive claim** with unique token, owner, collision safety, recheck and conditional release for issues and a shared PR exclusion domain. A label or assignee is never an atomic claim. Block mutation if the adapter cannot guarantee exclusivity.
3. Persistent candidate identity/stage, accepted plan reference when project policy requires it, and approvals bound to the issue/plan or exact diff revision. Resume the same authorized branch/PR, including closed-unmerged cases.
4. Real test/CI commands and recorded outcomes, structured reviews and inline comments, authorization for issue/PR writes and protected merging.
5. Desktop-safe test execution per [canonical policy](WORKING-LOOP.md#desktop-safe-test-execution): classify actual command effects and required fidelity, provide non-disruptive default and explicitly gated headed/full entrypoints, verify isolated runner or scoped human authorization, fail closed before disruptive effects, enforce exclusive use and bounded cancellation/cleanup, preserve required evidence. Host enforcement, not skill prose, controls permissions. Qualify denial, contention and cleanup; integrate runner provenance and evidence invalidation with the convergence ledger.
6. Review convergence per [canonical policy](WORKING-LOOP.md#review-convergence-and-evidence-reuse): durable candidate-wide finding/cycle ledger across workers, independent review provenance, impact-based rechecks, escalation and final exact-head approval. Do not reset the three-cycle budget or execute duplicate headed suites merely because review stage changes. Existing stricter requirements remain binding.
7. One authoritative source for milestone implementation plan and complete GitHub snapshot to feed the dashboard renderer. The renderer does not fetch GitHub.

Do not advertise an operational end-to-end workflow before these adapters and live tests exist. See [SDLC-DESIGN.md](SDLC-DESIGN.md) for goals and non-goals.
