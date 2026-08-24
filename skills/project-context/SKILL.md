---
name: project-context
description: Retrieve the smallest trustworthy project context needed for an SDLC task without treating summaries or agent memory as project truth.
---

# Project context

## When to use

Use when a task depends on project-specific requirements, architecture, decisions, components, constraints, risks, current work state, or relationships between them and loading the whole repository would be wasteful.

## Do not use

- Do not treat a context summary, vector/search result, agent memory, or conversation history as project authority.
- Do not copy the whole repository into durable context merely to avoid retrieval decisions.
- Do not persist transient reasoning, secrets, speculative conclusions, or unverified assumptions as facts.
- Do not silently reconcile conflicting authoritative sources.

## Required context

Start with the task itself and the project's context/index configuration. Query only for the concepts materially needed for the current activity: component names, requirement/decision IDs, risk areas, work items, milestones, or other relevant entities.

Project context is a navigation/index layer. It never overrides authoritative requirements, decisions, specifications, code, tests, approved decisions, or tracker/work-state authority. When a summary disagrees with its source, the source wins and the summary is stale.

## Stop or escalate when

- **Stale source:** stop relying on the stale summary; read the current source and refresh/rebuild the derived index.
- **Dangling/invalid relationship:** treat the graph/index as invalid and fall back to authoritative-source search.
- **Conflicting authoritative sources:** route to the appropriate reconciliation/decision activity; do not choose silently.
- **No useful match:** broaden once, then use targeted repository/artifact search instead of guessing from memory or loading everything.

## Procedure

1. Determine the smallest concepts needed for the current task.
2. If the project has `.sdlc/graph/context-index.json`, query it with the reference tool when available:

   ```sh
   python3 <ai-sdlc-root>/tools/project_context.py --root <project-root> query <terms>
   ```

3. Validate the derived index before relying on it for consequential architecture, planning, or implementation decisions:

   ```sh
   python3 <ai-sdlc-root>/tools/project_context.py --root <project-root> validate
   ```

4. Load compact context first: node/entity ID, kind, summary, relationships, source paths, and staleness status.
5. Follow only the relationships needed to understand the current task. Prefer one-hop expansion before broad search.
6. Read the authoritative source artifacts returned for any node that materially constrains a decision or implementation.
7. If the index is missing, stale, contradictory, or incomplete, search `.sdlc/context/` and authoritative project artifacts directly.
8. Persist new durable context only when it is backed by an authoritative source and the project's context-curation rules permit it.

## Output contract

Return or expose the smallest useful context slice:

```text
query_terms
matched_entities: id + kind + concise summary
relationships_needed
source_paths
staleness_or_conflict_status
fallback_or_next_search (when needed)
```

A retrieved summary is navigation evidence, not permission to skip its authoritative source for consequential work.

## Handoff

Pass the compact context slice and source references to the active SDLC skill. If retrieval reveals stale/conflicting authority, hand off to reconciliation/decision work before implementation or verification continues.

The generic skill owns retrieval semantics only. A consuming project owns its `.sdlc/` data, project-specific agent instructions, and domain-specific skills.
