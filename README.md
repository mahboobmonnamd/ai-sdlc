# AI-SDLC

AI-SDLC is an open, generic suite of reusable Agent Skills for disciplined AI-assisted software development.

Its goal is to make AI-assisted development behave like strong software engineering: reduce ambiguity before implementation, preserve explicit decision authority, keep work scoped, require evidence, and make routing between planning, implementation, review, remediation, and verification deterministic.

## Model

~~~text
SKILL   = how a reusable SDLC activity is performed
CONTEXT = what is currently true about a project
TOOL    = deterministic retrieval/validation/evidence support
AGENT   = optional coordinator; not required for core skills
~~~

Project requirements, approved decisions, specifications, code, tests, tracker state, and explicit human/product authority remain authoritative. AI-SDLC context is navigation/provenance support, never a replacement source of truth.

## Current skill catalog

- project-context — retrieve the smallest trustworthy project context;
- work-item-design — create/refine one independently reviewable work item;
- implementation-planning — produce/version a durable **proposed** implementation plan without accepting it or changing product authority;
- development-readiness — decide whether implementation may begin (requires accepted plan + acceptance evidence) and produce actionable gaps when it may not;
- implementation — execute or resume one identified, ready, planned work item on its authorized candidate, with ownership/candidate lifecycle governance;
- verification — prove acceptance outcomes from reproducible evidence;
- pr-review — perform the complete full-candidate implementation + merge-readiness review (usable standalone; plan required only when policy/workflow requires it);
- address-pr-review — batch-remediate review-stage PR review/check failures, then hand back to full PR review (or to implementation if still incomplete).

There is intentionally no separate generic code-review skill. Keeping implementation-defect review inside pr-review removes ambiguous routing when a user simply asks to “review PR N”.

## Core workflow

~~~text
work-item-design
→ implementation-planning          (PROPOSED plan)
→ plan acceptance                  (project technical authority)
→ development-readiness
→ implementation                   (IMPLEMENTATION_IN_PROGRESS)
→ host/project merge-candidate handoff
→ pr-review                        (IN_REVIEW)
   ├─ READY_TO_MERGE
   └─ CHANGES_REQUIRED → address-pr-review → pr-review
~~~

verification can be invoked independently and is also consumed by pr-review.

Evaluation layout: per-skill unit contracts under `evals/unit/`, multi-skill integration under `evals/integration/core-development-loop.json`, layout index at `evals/core-development-loop.json`. CI validates contract schema and rejects self-certification checks. `tools/eval_judge.py` scores real output fields; the integration runner compares `observed_route` with `expected_route`. Behavioral evaluation remains `NOT_RUN` until a live skill adapter executes.

See docs/WORKING-LOOP.md for invocation and governance semantics.

## Quality model

Every publishable skill must have:

- a clear invocation contract and required identifier/input;
- positive and negative routing boundaries;
- required evidence/context;
- explicit stop/escalation behavior;
- a deterministic procedure/workflow;
- a reproducible output/verdict contract;
- an explicit handoff/next activity;
- evaluation scenarios with expected and forbidden behaviors;
- deterministic catalog validation in CI;
- no dependency on one product, tracker, language, framework, or agent vendor.

Run:

~~~sh
make check
~~~

## skills.sh

The target distribution is skills.sh / the open Agent Skills ecosystem. Once publication gates pass:

~~~sh
npx skills add mahboobmonnamd/ai-sdlc
~~~

**Current status: not yet declared publish-ready.**

## Reference consumer

Seyal is the first demanding reference consumer. It keeps tracker/product/domain-specific governance in its own thin facades while consuming generic AI-SDLC capabilities through a reviewed pin. Generic capabilities must remain useful without Seyal.

## Design authority

- docs/ai-native-sdlc-skills-prd-v0.2.md
- Phase-0 design records under phase-0/
- Evaluation standard: phase-0/P0-07-evaluation-standard.md
- Core workflow: docs/WORKING-LOOP.md
- Consumer absorption map: docs/CONSUMER-ABSORPTION.md

## Contribution principle

Do not add a skill merely because a workflow can be written as a prompt. Add/change a skill only when it represents a coherent reusable capability with a clear routing boundary and realistic evaluation cases. Prefer one obvious user-facing skill per lifecycle intent over overlapping skills that force agents to guess.
