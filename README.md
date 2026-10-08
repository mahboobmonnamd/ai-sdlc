# AI-SDLC

A small, reviewable suite of skills for issue-to-merge engineering workflows.

## Commands

| Skill | Purpose | Approval |
| --- | --- | --- |
| `/create-issue` | Refine an idea, asking one material question at a time, until the Definition of Ready is met | Author approves issue draft |
| `/implement-issue <N>` | Exclusive claim → readiness/plan → code/tests → PR | **Gate 1** before coding, **Gate 2** before push/PR |
| `/pr-review <N>` | Independent full-head review with inline GitHub comments | Approve or request changes |
| `/process-review <N>` | Triage and fix the complete review feedback set | **One gate** before changes |
| `/pr-merge <N>` | Merge approved, current head only when checks/protections pass | Existing repository merge authority |
| `/describe-backlog [milestone]` | Ready, blocked and active issue inventory | Read-only |
| `/whatsnextfor-me [milestone]` | Recommend one unclaimed ready issue | Read-only |
| `/projectstatus [milestone]` | Plan-versus-issues reconciliation and self-contained HTML dashboard | Read-only |

`project-context` and `verification` remain reusable support skills, not extra lifecycle gates.

## Main loop

```text
/create-issue → /implement-issue → /pr-review
                                       │
                   APPROVE ────────────┴──→ /pr-merge
                   REQUEST_CHANGES ────→ /process-review → /pr-review
```

GitHub labels show workflow state, **not exclusive ownership**. Atomic claims prevent concurrent agents acting on the same issue/PR. Stage transitions, all twelve readiness checks, approvals and safety rules are in [the working loop](docs/WORKING-LOOP.md).

Use `make check` for structural, test and evaluation-contract validation. These checks do not replace live behavioral evaluation; evaluation results remain `NOT_RUN` until real adapters are executed.

The design is intentionally focused: no separate planning, development-readiness, implementation, or review-remediation entrypoints. Implementation plans live inside their issues unless a project explicitly requires otherwise.

Earlier Phase-0 records remain historical design context. The current workflow is defined here and in `docs/WORKING-LOOP.md`. Existing consumers must update their pinned skill names deliberately.
