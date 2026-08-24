# P0-09 — Project-context reference capability and consumer boundary

**Phase:** 0 reference implementation  
**Status:** Proposed by Issue #1  
**Depends on:** P0-02 context data model, P0-03 staleness/invalidation, PRD v0.2

## 1. Purpose

Define how the generic AI-SDLC project-context capability is packaged and consumed without turning every product repository into a fork of the SDLC workflow.

## 2. Authority model

The authority chain remains:

```text
authoritative project artifacts
(requirements / ADRs / specs / code / tests / approved decisions)
        ↓ provenance
.sdlc/context/*.yaml
(canonical portable SDLC serialization)
        ↓ optional derived view
.sdlc/graph/context-index.json
(compact navigation/cache only)
        ↓
project-context skill / agents
```

The derived JSON index is never authoritative. Its purpose is fast, low-context retrieval. It must fail visibly when source fingerprints, relationships, or source paths are stale/invalid.

## 3. Generic ownership

The `ai-sdlc` repository owns:

- the reusable `project-context` skill;
- context retrieval semantics;
- validation/staleness behavior for the optional derived index;
- the reference `tools/project_context.py` implementation;
- generic schema/evaluation guidance.

A consuming product repository owns:

- its authoritative product/architecture/code/test artifacts;
- its `.sdlc/` project data and derived index;
- project-specific agent instructions;
- domain-specific skills that require product knowledge.

Generic SDLC procedures should not be copied into each consuming repository.

## 4. Consumption pattern

Until a package/registry mechanism is finalized, the deterministic reference integration is a **pinned Git dependency/submodule** plus a thin project-local discovery adapter.

Conceptually:

```text
project/
├─ .sdlc/
│  ├─ framework/                # pinned ai-sdlc revision
│  ├─ context/                  # project-owned YAML context
│  └─ graph/context-index.json  # project-owned derived navigation index
└─ .agents/skills/project-context/SKILL.md
   # thin adapter that delegates to .sdlc/framework/skills/project-context
```

The pin is reviewed like any other development dependency. Product build/runtime paths must not require AI-SDLC.

## 5. Migration rule for existing project skills

Do not move every existing project skill to AI-SDLC at once.

Migrate a skill only when:

1. its procedure is genuinely reusable across unrelated products;
2. all product-specific assumptions can be supplied as project context or a thin adapter;
3. the generic version has tests/evaluation cases;
4. the consuming repository can pin/version it deterministically; and
5. migration does not weaken product-specific engineering gates.

Good migration candidates include generic issue refinement, implementation workflow, code review, verification, documentation lifecycle, security/performance review orchestration, and project-context retrieval. Domain skills such as terminal conformance, VT TDD, Metal rendering, or a product's architecture invariants remain with the product.

## 6. Seyal as reference consumer

Seyal is an appropriate first integration because it has strict architecture ownership, TDD/conformance/performance requirements, OSS/commercial boundaries, and multiple coding-agent clients. The reference integration should prove that AI-SDLC reduces context loading without weakening any Seyal-specific authority or quality gate.

Seyal-specific knowledge must not be copied into this repository merely to support the integration.

## 7. Validation expectations

A consumer integration should prove at minimum:

- pinned AI-SDLC revision is explicit;
- generic skill is discoverable through a thin local adapter;
- derived context index validates against current authoritative source fingerprints;
- stale/missing/dangling context fails visibly;
- generic tooling is absent from product/runtime dependency paths;
- project-specific skills continue to override generic guidance where domain authority is required.
