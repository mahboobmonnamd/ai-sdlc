---
name: project-context
description: Retrieve the smallest trustworthy project context needed for an SDLC task without treating summaries or agent memory as project truth.
---

# Project context

Use this skill when a task depends on project-specific requirements, architecture, decisions, components, constraints, current work state, or relationships between them and loading the whole repository would be wasteful.

## Authority

Project context is a navigation/index layer. It never overrides authoritative requirements, ADRs, specifications, code, tests, approved decisions, or tracker state. When an index summary disagrees with its source, the source wins and the index is stale.

## Retrieval workflow

1. Determine the smallest concepts needed for the current task: component names, requirement/decision IDs, risk area, work item, or milestone.
2. If the project has `.sdlc/graph/context-index.json`, run the reference query tool when available:

   ```sh
   python3 <ai-sdlc-root>/tools/project_context.py --root <project-root> query <terms>
   ```

3. Validate the index before relying on it for architecture or implementation decisions:

   ```sh
   python3 <ai-sdlc-root>/tools/project_context.py --root <project-root> validate
   ```

4. Read the authoritative source files returned for the relevant nodes before making or changing a decision. Do not treat the compact summary as sufficient authority for a consequential change.
5. Follow relationships only as far as needed for the task. Prefer one-hop related context before broad repository search.
6. If the index is missing, stale, contradictory, or has no useful match, perform a targeted search of `.sdlc/context/` and authoritative repository artifacts. Do not guess from conversation memory.
7. Persist new durable context only when it is backed by an authoritative source and the project's context-curation rules allow it. Do not store transient reasoning, speculative conclusions, secrets, or unverified assumptions as facts.

## Progressive disclosure

Return or load compact context first:

```text
node id + kind + summary
relationships
source paths
staleness status
```

Open full source artifacts only for nodes that materially affect the task.

## Failure behavior

- **Stale source:** stop relying on the stale summary; read the current source and refresh/rebuild the derived index.
- **Dangling relationship:** treat the graph as invalid and fall back to authoritative-source search.
- **Conflicting authoritative sources:** do not reconcile silently; route to the appropriate SDLC decision/reconciliation activity.
- **No match:** broaden the query once, then use targeted repository search rather than loading the entire codebase.

## Generic/project boundary

This skill and its retrieval semantics are generic AI-SDLC capability. A consuming project owns its `.sdlc/` data, project-specific agent instructions, and domain-specific skills. Do not copy project knowledge into this generic skill.
