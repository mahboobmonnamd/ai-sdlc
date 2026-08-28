# AI-SDLC

AI-SDLC is an open, generic suite of reusable Agent Skills for disciplined AI-assisted software development.

Its goal is not to make agents write more code. Its goal is to make AI-assisted development behave more like strong software engineering: reduce ambiguity before implementation, preserve explicit decision authority, keep work scoped, require evidence, and separate implementation confidence from verification.

## Model

```text
SKILL   = how a reusable SDLC activity is performed
CONTEXT = what is currently true about a project
TOOL    = deterministic retrieval/validation/evidence support
AGENT   = optional future coordinator; not required for core skills
```

Project requirements, approved decisions, specifications, code, tests, and explicit human/product authority remain authoritative. AI-SDLC context is navigation/provenance support, never a replacement source of truth.

## Current skill catalog

The first reference slice contains:

- `project-context` — retrieve the smallest trustworthy project context;
- `development-readiness` — decide whether implementation may begin and route blockers;
- `work-item-design` — create one implementation-ready, independently reviewable unit of work;
- `implementation` — execute ready work without silently changing authority or scope;
- `code-review` — independently review implementation and evidence;
- `verification` — prove acceptance outcomes separately from implementation/review confidence;
- `pr-acceptance-review` — independently synthesize exact-revision authority, implementation, verification, checks, measurements, documentation, and residual risk into a merge-readiness verdict.

This is intentionally not the complete PRD catalog yet.

## Quality model

Every publishable skill must have:

- clear positive and negative routing boundaries;
- required evidence/context;
- explicit stop/escalation behavior;
- a reproducible output/verdict contract;
- right-sized rigor rather than universal ceremony;
- evaluation scenarios with expected and forbidden behaviors;
- deterministic catalog validation in CI;
- no dependency on one product, tracker, language, framework, or agent vendor.

Run:

```sh
make check
```

## skills.sh

The target distribution is skills.sh / the open Agent Skills ecosystem. Once the publication gate in [`docs/PUBLISHING.md`](docs/PUBLISHING.md) passes, users will be able to install the repository with:

```sh
npx skills add mahboobmonnamd/ai-sdlc
```

Individual skill selection can use the skills CLI's supported `--skill` option where appropriate.

**Current status: not yet declared publish-ready.** The repository is still proving the initial skill loop against evaluation contracts and a real reference consumer.

## Reference consumer

Seyal is the first demanding reference consumer. It keeps terminal/product-specific knowledge and skills in its own repository while consuming generic AI-SDLC capabilities through a reviewed pin. Generic capabilities must remain useful without Seyal.

## Design authority

- [`docs/ai-native-sdlc-skills-prd-v0.2.md`](docs/ai-native-sdlc-skills-prd-v0.2.md)
- Phase-0 design records under [`phase-0/`](phase-0/)
- Evaluation standard: [`phase-0/P0-07-evaluation-standard.md`](phase-0/P0-07-evaluation-standard.md)

## Contribution principle

Do not add a skill merely because a workflow could be written as a prompt. Add or change a skill only when it represents a coherent reusable capability, has a clear routing boundary, and can be evaluated against realistic failure cases.