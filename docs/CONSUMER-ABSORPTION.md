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

## Required adapter capabilities

1. Fresh, paginated issue/PR/CI/review/branch retrieval, exact head and dependency graph.
2. **Real atomic exclusive claim** with unique token, owner, collision safety, recheck and conditional release for issues and a shared PR exclusion domain. A label or assignee is never an atomic claim. Block mutation if the adapter cannot guarantee exclusivity.
3. Persistent candidate identity/stage, accepted plan reference when project policy requires it, and approvals bound to the issue/plan or exact diff revision. Resume the same authorized branch/PR, including closed-unmerged cases.
4. Real test/CI commands and recorded outcomes, structured reviews and inline comments, authorization for issue/PR writes and protected merging.
5. One authoritative source for milestone implementation plan and complete GitHub snapshot to feed the dashboard renderer. The renderer does not fetch GitHub.

Do not advertise an operational end-to-end workflow before these adapters and live tests exist. See [SDLC-DESIGN.md](SDLC-DESIGN.md) for goals and non-goals.
