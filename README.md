# AI-SDLC

**Objective:** Reduce time from implementation-ready issue to safely merged PR by eliminating redundant handoffs, avoiding duplicate work, and closing review feedback in batches—without weakening engineering quality.

- [Engineering design brief](docs/SDLC-DESIGN.md): rationale, recovery guarantees, user-interruption budget, measurable outcomes.
- [Canonical working loop](docs/WORKING-LOOP.md): 12-point Definition of Ready, claim safety, lifecycle, approvals and evidence.

## Task-first workflow

Choose LIGHTWEIGHT / STANDARD / CRITICAL from actual impact, not file extension. Read only the active skill and relevant policy sections; preserve the user's problem as primary context. Use one evidence packet, one accountable independent review by default, and existing deterministic CI checks. See [task-first policy](docs/WORKING-LOOP.md#task-first-execution-and-progressive-context). Existing mandatory consumer checks and protections still apply. For selective reads, use `python3 tools/read_policy.py --list`, then pass only the applicable section IDs; no new gate or mandatory tool call.

## Commands

| Command | Work | Human decision |
| --- | --- | --- |
| `/create-issue` | Turn an idea into a testable issue; ask only one material question at a time | Approve issue draft |
| `/implement-issue <N>` | Readiness + plan → atomic claim → implement/tests → verified PR | Gate 1 plan, Gate 2 push/PR |
| `/pr-review <N>` | Independent risk-proportional whole-candidate review; findings only when justified | Approve or request changes |
| `/process-review <N>` | Triage and fix all comments and failing checks in a batch | One remediation gate |
| `/pr-merge <N>` | Merge exact independently approved head after checks/protections | Explicit invocation |
| `/describe-backlog [milestone]` | Live ready/blocked/active issues | Read-only |
| `/whats-next-for-me [milestone]` | Recommend one unclaimed ready issue | Read-only |
| `/projectstatus [milestone]` | Reconcile implementation plan with current GitHub; generate HTML dashboard | Read-only |

`project-context` and `verification` remain internal supporting skills, **not additional user-facing gates**.

```text
create-issue → implement-issue → pr-review ── APPROVE ──→ pr-merge
                                      └── REQUEST_CHANGES ──→ process-review
                                                                   │
                                                 impact recheck + final review ←─┘
```

**Preserved from the original system:** governance and accepted-plan authority, safe resume of existing/closed-unmerged candidates, no duplicate PRs, explicit ownership, exact-revision verification, risk-based tests, independent whole-candidate exact-head review and protected merging. Separate mandatory planning/readiness ceremonies are removed; issue contains the plan unless project policy says otherwise.

**Test execution:** [desktop-safe by default](docs/WORKING-LOOP.md#desktop-safe-test-execution). Isolate interactive automation or require explicit bounded per-run permission where allowed. Coordinate required native suites with review convergence; never waive mandatory evidence or reuse desktop authorization.

Run `make check` for catalog, evaluation contracts, CI and unit checks. This is not proof of live multi-agent execution: behavioral evaluations remain `NOT_RUN` until real adapters and claim handling are exercised. Consumers must integrate GitHub permissions, a transactional claim backend and actual test execution.

[Review convergence](docs/WORKING-LOOP.md#review-convergence-and-evidence-reuse): batch blockers, focus interim rechecks on impacted behavior, independently verify whole-candidate acceptance at final head, escalate after three routine remediation cycles or earlier no-progress/unsafe conditions. No stale approvals or weaker merge gates. Consumers must update reviewed pins and reconcile stricter local rules; policy alone does not interrupt an already running agent.
