---
name: create-issue
description: Interview an issue author and prepare a Definition-of-Ready issue one question at a time; not for coding or silently deciding product behavior.
---

# Create issue

## Invocation contract
Input: rough idea, requested change, or existing issue number. An existing issue is edited only with user authorization.

## When to use
Use to turn an idea or incomplete issue into one independently testable implementation issue.

## Do not use
Do not invent product decisions, impose a long questionnaire, mark ready with unresolved blockers, or create duplicates.

## Required context
Read the relevant repository requirements, known decisions, related issues, code contracts, dependencies, and the shared Definition of Ready in `docs/WORKING-LOOP.md`.

## Stop or escalate when
A question needs product/security/architecture authority, a duplicate already covers the outcome, or an item is too broad to verify independently.

## Procedure
1. Search for duplicates and existing decisions before asking.
2. Ask **one material question per turn**, with your recommended answer and why. Skip questions already answered by authoritative context.
3. Prefer plain language, observable current versus desired behavior, negative cases and explicit exclusions. Split only genuinely independent outcomes.
4. Build the implementation plan as a short ordered sequence inside the issue; do not require a separate planning artifact.
5. Validate **all 12** Definition-of-Ready checks, including design nuance and open `!+concern` issues, dependencies, congruence and security controls.
6. Display the final issue draft and readiness table. Create or update the issue only when the author approves that draft.
7. Add `needs:implementation` only when every mandatory check passes. Unready work stays in refinement; optional verification command may be absent.

## Output contract
Return: issue title/body, current-versus-expected behavior, scope/non-goals, acceptance checklist, implementation plan, dependency links, security assessment, readiness table (PASS/FAIL/UNKNOWN/N/A), outstanding single next question, and created/updated issue link when applicable.

## Handoff
Ready → `implement-issue`. Missing decision → record concern and continue refinement; never disguise it as ready.
