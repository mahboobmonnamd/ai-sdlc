# Canonical working loop

Use exactly one user-facing skill per intent. The issue is the plan. Projects may add domain requirements but must not weaken claim, evidence, approval or security gates.

## 12-point Definition of Ready (DoR)

Every issue must have the following, with an explicit PASS / FAIL / UNKNOWN / N/A result:

| # | Check | Passing condition |
| --- | --- | --- |
| 1 | Problem stated | Clear why the change is needed and for whom |
| 2 | Observable behavior | Concrete current vs expected behavior, including important failure cases; enough to write tests |
| 3 | Bounded scope | In scope and out of scope are explicit |
| 4 | Verifiable acceptance criteria | Independently checkable outcomes, not vague adjectives |
| 5 | Verification command (optional) | Useful commands provided when known; absence does not block if the evidence approach is clear |
| 6 | Design decisions closed | Agreed choices recorded under `## Design nuance`; unresolved choices linked/tagged `!+concern` and block if material |
| 7 | Congruence | Consistent with product intent, code ownership and accepted architectural/security decisions |
| 8 | Dependencies | All blockers identified and complete, or explicitly sequenced without unsafe assumptions |
| 9 | Not duplicate | Search confirms no other issue/PR already implements the same change |
| 10 | Self-contained | A competent implementer can work from this issue and linked authority without hidden chat context |
| 11 | Implementation plan | Ordered, bounded implementation steps and acceptance-to-test mapping inside the issue |
| 12 | Security controls | Trust boundaries, inputs, authz, secrets, privacy, logging, dependency or abuse risks evaluated; N/A justified |

Do not mark an issue READY when required items are FAIL/UNKNOWN. The verification **command** is optional; testing/evidence is mandatory. Do not invent closed decisions. Missing designs get one targeted question (via `create-issue`) or an explicit concern.

## Lifecycle and labels

```text
needs:implementation --[exclusive claim]--> issue:implementing
    --[gate1 yes, code/test, verification, gate2 yes]--> needs:review (PR)
needs:review --[exclusive claim]--> pr:reviewing
    --[approve exact SHA]--> needs:merge
    --[request changes]--> needs:processing
needs:processing --[exclusive claim]--> pr:processing
    --[gate yes, fix+verify]--> needs:review
needs:merge --[revalidate exact reviewed SHA, checks, protections]--> merged
```

Treat stage labels as **visibility only**. Claim operations are separate and must not be implemented as a read-then-write label swap. `needs:review`, `pr:reviewing`, `needs:processing` and `pr:processing` must not coexist on the same PR. Transition only after the owner is verified; cleanup only labels owned by the current transition. A failed label API call must be reported and reconciled, never silently ignored.

## Exclusive claim protocol

- Atomically acquire a resource-keyed claim, e.g. `issue:<N>:implement` or `pr:<N>:review` / `pr:<N>:process`. Review and processing for the **same PR** share an exclusion domain `pr:<N>`, to prevent edits during review.
- A backend must support **create-if-absent** with an owner identity and unique claim token. One usable GitHub implementation is a fixed-name claim ref (one per resource) created through the Git Refs API: only one simultaneous creation succeeds (the other receives a conflict). Put owner/token into a claim commit; the ref must point to that commit. Another transactional lock service is acceptable.
- On acquire, re-read the claim record and verify owner/token before **any** state mutation, branch creation or file edit. Revalidate owner/token before each critical push, review or merge handoff. A label change or assignee update is **not** proof of exclusive ownership.
- Release only an owned claim. For Git ref locks, verify the exact current owner/token before deleting the ref; do not forcibly steal or reuse a claim. Stale-lock recovery needs an authorized explicit intervention/audit, not an automatic race-prone timeout.
- If the backend is unsupported, claim collision exists, or ownership is ambiguous, **fail closed**. Report the blocker and do not modify code/labels.
- Use the existing candidate/branch for resumes. Do not create parallel PRs for the same issue, including when a PR was closed without merging.

## Gates and evidence

**Implement Gate 1**: complete DoR table + validated short implementation plan; ask exactly "Proceed with implementation? (yes/no)". No branch or edits before yes. Work starts from current `origin/main` after approval, except authorized continuation on existing head.

**Implement Gate 2**: diffstat + exact base/head + every criterion mapped to a test/observable result + full proposed PR body with `Closes #N`; ask exactly "Push branch and create PR? (yes/no)". No push/PR before yes. Test failures never count as proof.

**Process review**: one decision table for every outstanding finding and failing required check, with dispositions `should fix`, `improvement`, `discard`, `disagree`, `push back`. Ask exactly "Apply this plan? (yes/no)" once before edits/push/replies/closing threads. Re-review entire head after verified remediation.

**Independent review**: inspect full diff and affected paths; use `[CRIT]`, `[SEC]`, `[NONCONF]`, `[IMPR]`, `[GOOD]`. Unresolved mandatory findings require REQUEST_CHANGES; non-blocking improvements alone allow APPROVE. Head changes invalidate approval.

**Merge**: current head must match approved head; required CI, protections, merge queue, blocking review threads and dependencies must pass. No administrative bypass. GitHub `Closes #N` closure is verified after merge, not assumed.

## Invariants

No product/security decision invented by agents. No cross-issue scope drift or weakened tests. Reproducible evidence is required; mark unavailable measurements UNKNOWN. Respect least privilege and do not publish secrets. Requests for missing authority stop with the exact issue/decision owner, not ritualized multi-question forms.
