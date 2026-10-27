# AI-SDLC

**Objective:** Reduce time from implementation-ready issue to safely merged PR by eliminating redundant handoffs, avoiding duplicate work, and closing review feedback in batches—without weakening engineering quality.

- [Engineering design brief](docs/SDLC-DESIGN.md): rationale, recovery guarantees, user-interruption budget, measurable outcomes.
- [Canonical working loop](docs/WORKING-LOOP.md): 12-point Definition of Ready, claim safety, lifecycle, approvals and evidence.

## Commands

| Command | Work | Human decision |
| --- | --- | --- |
| `/create-issue` | Turn an idea into a testable issue; ask only one material question at a time | Approve issue draft |
| `/implement-issue <N>` | Readiness + plan → atomic claim → implement/tests → verified PR | Gate 1 plan, Gate 2 push/PR |
| `/pr-review <N>` | Independent full-candidate review, inline evidence and findings | Approve or request changes |
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
                                                 full pr-review ←─┘
```

**Preserved from the original system:** governance and accepted-plan authority, safe resume of existing/closed-unmerged candidates, no duplicate PRs, explicit ownership, exact-revision verification, risk-based tests, full re-review and protected merging. Separate mandatory planning/readiness ceremonies are removed; issue contains the plan unless project policy says otherwise.

Run `make check` for catalog, evaluation contracts, CI and unit checks. This is not proof of live multi-agent execution: behavioral evaluations remain `NOT_RUN` until real adapters and claim handling are exercised. Consumers must integrate GitHub permissions, a transactional claim backend and actual test execution.
