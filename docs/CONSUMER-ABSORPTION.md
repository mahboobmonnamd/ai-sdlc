# Consumer adoption

AI-SDLC now exposes eight user-facing lifecycle/reporting skills plus two supporting skills (`project-context`, `verification`). Consumer projects should pin a reviewed revision and explicitly migrate aliases.

| Previous entrypoint | New route |
| --- | --- |
| `work-item-design` | `create-issue` |
| `implementation-planning` + `development-readiness` + `implementation` | `implement-issue` (plan within issue, two gates) |
| `address-pr-review` | `process-review` (one gate) |
| `pr-review` | `pr-review` (full diff, structured GitHub review) |
| Host-specific merge logic | `pr-merge` (still respects host authority) |
| Backlog/status facades | `describe-backlog`, `whatsnextfor-me`, `projectstatus` |

Project-specific adapters own issue labeling, milestone mapping, branch naming, review posting, and claim backend integration. Claims **must be atomic**, not simulated with GitHub label swaps. Do not recreate the old separate planning/readiness/remediation skills or copy their full text into always-on instructions.

For consumers pinned to old paths: retain their current pin until this change is reviewed and tested. Alias old commands only at the consumer boundary during migration, then remove those aliases. Historical Phase-0 docs are not the live routing contract.
