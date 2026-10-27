# Engineering workflow design — v2

## Outcome

Reduce lead time from **ready issue → tested PR → approved PR → merged** without shifting cost into regressions, duplicate work, hidden human decisions, or repeated review cycles.

This document is the design brief. It supersedes the initial high-level prompt; `docs/WORKING-LOOP.md` is the normative operational policy. Historical Phase-0 documents remain design history, not executable routing instructions.

## Experience contract

An engineer supplies an issue/PR number once. Skills retrieve authoritative project facts automatically and ask only for a **material decision that changes action**. Do not ask about preferences, formatting, or known choices. Build evidence and show a concise preview before irreversible/externally visible actions.

**Human interrupts:** (1) author approves issue draft; (2) implement Gate 1 approves the plan, (3) implement Gate 2 approves push/open PR, (4) process-review approves one batched remediation plan. `/pr-merge` is an explicit merge instruction; do not add a redundant approval prompt. No repeated approval for individual tests, individual comments, or predictable steps.

**Automatic:** fresh retrieval, duplicate/candidate check, ready check, plan validation, test selection, narrow tests during development, full verification before PR, review-trace reconstruction, CI lookup, and generated dashboard.

**Stop immediately** on conflicting product/security authority, ambiguous exclusive ownership, unsafe dependencies, untestable required acceptance, or misleading verification. When blocked, return a specific remedy, not another long questionnaire.

## End-to-end phases

| Command | Responsibility | Exit criteria / next |
| --- | --- | --- |
| `create-issue` | One-question-at-a-time refinement to a 12-check Definition of Ready; match implementation/test plan to acceptance | Issue draft approved, `needs:implementation` |
| `implement-issue <N>` | Read-only preflight and plan Gate 1; atomic claim; code + tests; proof and Gate 2; open/reuse PR | PR with acceptance evidence and `needs:review` |
| `pr-review <N>` | Independently review the whole current candidate, exact head, affected boundaries, evidence/CI | One structured review: APPROVE or REQUEST_CHANGES |
| `process-review <N>` | Inventory, classify and batch **all** review findings and check failures; one gate; remediate on same branch | Re-review requested for changed head, or named blocker |
| `pr-merge <N>` | Reconcile exact-head independent approval, checks, protections, threads and dependencies | Verified merge commit and linked issue closure |
| `describe-backlog` | Fetch complete filtered backlog; verify DoR, claims and dependencies | Ranked ready, active, blocked and incomplete inventory |
| `whats-next-for-me` | Select one highest-impact **unclaimed** ready issue from fresh backlog | Evidence-backed selection, not automatic assignment |
| `projectstatus` | Reconcile plan/milestone with GitHub issues/PRs; produce actual HTML artifact | Dashboard with gaps, health, links and trustworthy totals |

Support skills: `project-context` narrows authoritative retrieval; `verification` produces revision-bound criterion evidence. Neither adds a separate user-facing approval gate.

## Restore and preserve these previous safeguards

1. **Candidate continuity:** search open and closed-unmerged heads; resume same authorized head. Do not duplicate branches/PRs. A rejected architecture is never quietly resumed. Missing lifecycle identity is BLOCKED, not guessed.
2. **Source of truth:** issue plus accepted decisions/specs, tests, and code. The work item can serve as the plan. Require an independently versioned accepted plan only when an explicit project policy requires it; load that **exact** revision and acceptance evidence.
3. **Semantic staleness:** change to scope/acceptance, dependency, design or security authority invalidates Gate 1; claim labels, assignee, timestamps or routine comments alone do not.
4. **Risk-proportional evidence:** every acceptance criterion has proof; choose focused tests for low-risk changes, broader integration, negative, concurrency, migration and security tests for high-risk changes. Record commands, output and SHA. Do not claim "tested" because code compiles.
5. **Lifecycle boundaries:** unfinished implementation (including CI/early comments) stays in implement-issue. Post-review remediation belongs to process-review. Independent PR review never edits code.
6. **Security authority:** expose trust and data boundaries, authz, input/secret handling, privacy and abuse/failure risks; escalate unresolved decisions rather than silently choosing a solution.
7. **Review quality:** inspect complete changed behavior and impacted paths, not just changed lines; find all material root causes in one pass. Non-blocking improvement does not prevent approval.
8. **Merge correctness:** bind review, check results and evidence to exact current head. Respect branch protections, code owners and merge queue. Never use admin bypass to make a PR green.
9. **Auditability:** record who approved which plan/head and the command/output used for proof. Provide working links for side effects. Do not claim external mutations before tool confirmation.

## Throughput strategy

- **Front-load inexpensive checks:** duplicate, DoR, claim availability and dependency check before planning deep or writing code.
- **Defer exclusive claim until the user approves Gate 1** (read-only preflight first): prevents holding a lock through an unanswered prompt. Before any mutation revalidate issue/plan state and atomically claim, then change labels. During resume, verify existing owner and candidate before asking again.
- **Keep issue as single small plan:** 3–7 ordered implementation steps; map each criterion to a test and impacted file/boundary. Avoid a second generic planning document or plan-acceptance ceremony.
- **Develop test-first where useful:** narrow failing test → smallest permanent code change → targeted test → applicable project checks → verification matrix. No enormous mandatory template for trivial changes.
- **Anticipate review:** pre-PR self-review checks unintended diff, unhandled errors, coverage gaps, security, migrations, compatibility and documentation. This is NOT independent review or self-approval.
- **Batch remediation:** one full review → one complete disposition/approval gate → fix root causes + siblings in batch → full re-review. Avoid per-comment review ping-pong.
- **Never lower acceptance to reduce time.** Put genuinely unrelated optional improvements in separate follow-ups.
- **Recovery is cheap:** persist issue/PR/head/owner, gate approvals, current evidence, unprocessed comments and next action in the issue/PR or other authorized durable system; revalidate instead of replaying the entire workflow.

## Observable success measures

Track from GitHub events when available (avoid fabricated baselines):
- Ready → PR opened lead time; PR opened → merged lead time; waiting-for-human vs active execution.
- Review rounds per merged PR and repeat findings / reopened findings.
- PRs blocked by missing acceptance, ownership collisions, failing CI, stale heads.
- Post-merge regressions tied to a change (where source data exists).
- Number of redundant questions and duplicate candidates prevented.

Do not optimize only for tickets closed or agent actions minimized. Favor fewer interventions **and** fewer escaped defects.

## Intentionally excluded from the critical path

Mandatory separate planning/readiness skills; manual context summaries for every turn; repeated approvals for tests/comments; universal full E2E suites for trivial changes; separate generic code-review; automatic merge at the moment approval appears; speculative issue edits; and mandatory dashboard generation on every PR.

**Implementation note:** a skill definition does not itself provision GitHub permissions, a transactional claim adapter, test runtime, or issue/PR event automation. Callers must supply those. Do not claim the workflow is operational end-to-end until realistic tool-driven evaluations cover them.
