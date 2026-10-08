---
name: implement-issue
description: Claim, plan, implement, verify and propose a pull request for one ready issue using two explicit approval gates; not for review remediation or merging.
---

# Implement issue

## Invocation contract
`/implement-issue <Issue>` requires the issue number; identify repository from current project. No implicit issue selection.

## When to use
Use for `needs:implementation` issues or to resume the same authorized incomplete implementation.

## Do not use
Do not modify another owner's work, create parallel candidates, decide open design questions, push before gate 2, or bypass required tests.

## Required context
Fetch issue and dependencies fresh, approved decisions, plan, relevant code/tests, branch policy, claim state, existing branches/PRs, and the shared Definition of Ready.

## Stop or escalate when
A mandatory readiness item fails; an unresolved `!+concern` affects this issue; a dependency is blocked; claim is held by someone else; plan contradicts accepted authority; or verification fails.

## Procedure
1. **Claim**: atomically obtain exclusive ownership for issue N following `docs/WORKING-LOOP.md`; a failed competing claim must stop. After confirming ownership, transition `needs:implementation` → `issue:implementing`. Labels alone are not a lock.
2. **Readiness**: evaluate all 12 checks, including testable current/expected behavior and the security controls. Verification command is optional; proof is not.
3. **Plan**: inspect production integration seams; validate issue's implementation plan against scope, dependencies, rollback and acceptance tests. Keep the plan in the issue; note improvements in the preview instead of silently changing scope.
4. **Gate 1**: show the complete readiness table, blockers, concise execution plan and proposed test commands. Ask **"Proceed with implementation? (yes/no)"**. Do not create branch/edit code until yes. On no, release the claim and restore eligibility label if unchanged by others.
5. **Implement**: fetch `origin/main` and branch from that exact commit (unless repository explicitly sets another target). Resume the authorized existing branch/PR instead of creating duplicates. Implement only approved scope; write/run tests.
6. **Verification gate**: run reproducible acceptance, regression and risk-relevant checks. Map every acceptance criterion to command/output or observable evidence. Mark not-run honestly and stop on mandatory failures.
7. **Gate 2**: show exact branch/base/head, diffstat, criterion→evidence table, risks and full proposed PR title/body including `Closes #N`. Ask **"Push branch and create PR? (yes/no)"**. Do not push or open PR without yes.
8. **Open PR**: recheck claim and base, push same branch, create one non-draft PR targeting main with `Closes #N`, apply `needs:review`, remove `issue:implementing` as policy permits, and release the issue claim. Never assert PR creation without the returned URL.

## Output contract
Return: issue N, claim owner/state, readiness table, validated plan, gate responses, branch/base/head, tests and results, diffstat, acceptance/evidence matrix, PR body, and PR URL or a precise blocked reason.

## Handoff
Opened PR → `pr-review`. Review-stage fixes → `process-review`. Unready issue → `create-issue`.
