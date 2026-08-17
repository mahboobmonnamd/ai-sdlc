# Phase 0 Project Kickoff

**Project:** AI-Native SDLC Skills Suite  
**Phase:** 0 — Architecture & Design  
**Start Date:** 2026-08-17  
**Duration:** 3-4 weeks  
**Confidence Gate:** P0-09 Integrated Lifecycle Validation

---

## Executive Summary

Phase 0 translates v0.2 PRD requirements into concrete architectural specifications. The phase is organized into **8 design workstreams + 1 validation workstream**, each producing design + examples + test cases (not production code).

**Success Criteria:** End of Phase 0, all 9 workstreams deliver. P0-09 runs 6 representative scenarios through all designs with no conflicts detected. Phase 1 team has explicit answers to architecture questions without needing to guess or invent.

---

## Phase 0 Structure

### 8 Design Workstreams

| WS | Name | Status | Design Owner | PRD Link |
|---|---|---|---|---|
| **P0-01** | Routing & Precedence | Not Started | TBD | FR-010, FR-026, Section 7.4 |
| **P0-02** | Context Data Model | ✅ Design Complete | (complete) | FR-014, FR-015, Section 12.8 |
| **P0-03** | Staleness & Invalidation | Not Started | TBD | FR-016, Section 12.10 |
| **P0-04** | Multi-Agent Consistency | Not Started | TBD | FR-034, Section 12.11 |
| **P0-05** | Resumability | Not Started | TBD | FR-035, Section 12.12 |
| **P0-06** | Rigor Profiles | Not Started | TBD | FR-031, Section 18.1 |
| **P0-07** | Evaluation Standard | Not Started | TBD | FR-020, FR-036, Section 20.3 |
| **P0-08** | Decision Escalation | Not Started | TBD | FR-028, Section 9.24 + new |

### 1 Validation Workstream

| WS | Name | Status | Owner | Depends On |
|---|---|---|---|---|
| **P0-09** | Integrated Lifecycle Validation | Not Started | TBD | All 8 WS complete |

---

## P0-02 Design: Context Data Model — DELIVERED

**Output:** `phase-0/P0-02-context-data-model.md`

**Decisions Made:**

1. **Canonical Format: YAML**
   - Authoritative storage format: `.sdlc/context/*.yaml` (one file per entity kind)
   - JSON export: Optional read-only view (regenerated from YAML)
   - No parallel representations; YAML is single source of truth
   - Rationale: Human-readable, git-friendly, nested structure matches entity relationships

2. **Logical Data Model**
   - Entity kinds: requirement, nfr, decision, specification, spike, spike_finding, work_item, milestone, verification, risk, handoff, decision_escalation, component, context_fact
   - Minimal fields per entity: id, kind, status, summary, source, authority, created_at, last_validated, relationships, depends_on, affects
   - Relationship types: requires, implements, depends_on, blocks, supersedes, governed_by, specified_by, verified_by, part_of, contains, contradicts, related_to

3. **Staleness Model**
   - validation_status: current|stale|needs_recheck|conflicted
   - last_validated timestamp + source_commit
   - depends_on: list of entities whose change invalidates this
   - affects: list of entities that become stale if this changes
   - invalidated_by: chain of what change made this stale

4. **Schema Versioning**
   - Semantic versioning: MAJOR.MINOR.PATCH
   - Backward-compatibility rules defined
   - Migration path example (v1.0.0 → v2.0.0)

**Worked Example Included:**
- Greenfield web app project with requirements, decisions, relationships
- Staleness cascade example (ADR change → affected entities)
- Full directory structure and file examples

**Ready for Phase 1:** Context storage implementation can now begin

---

## Phase 0 Workstream Dependencies

```
P0-02 (Context Data Model) ← LOCKED
    ↓
    ├→ P0-01 (Routing)           [decision_escalation state now defined]
    ├→ P0-03 (Staleness)         [invalidation cascade model exists]
    ├→ P0-04 (Multi-Agent)       [schema for conflict detection ready]
    ├→ P0-05 (Resumability)      [work_item/active_work entities defined]
    ├→ P0-06 (Rigor Profiles)    [entity kinds mapped to profiles]
    ├→ P0-08 (Decision Escalation) [decision_escalation entity structure known]
    │
    └→ P0-07 (Evaluation)        [independent]

All 8 ↓
    │
    ↓
P0-09 (Integrated Lifecycle Validation)
    ├→ Run greenfield scenario
    ├→ Run brownfield scenario
    ├→ Run interrupted-session scenario
    ├→ Run conflicting-agents scenario
    ├→ Run stale-context scenario
    └→ Run lightweight-project scenario
```

**Critical Path:** P0-02 (complete) → P0-01 & P0-07 (can start now) → Others (sequential)

---

## Immediate Next Steps

### Week 1 of Phase 0 (Aug 17-23)

**Parallel streams:**

1. **P0-01: Routing & Precedence** (Start Now)
   - [ ] Define precedence cascade (blocker → authority → uncertainty → artifact → ready)
   - [ ] Create decision table for all routing states
   - [ ] Worked example: vague idea → navigate through full lifecycle
   - [ ] Design ambiguity resolution (when >1 equally-valid next step)
   - [ ] Target completion: ~5 days

2. **P0-07: Evaluation Standard** (Start Now)
   - [ ] Define eval contract format (JSON schema)
   - [ ] Define baseline scoring rubric (dimensions, measurement methods)
   - [ ] Define passing thresholds + regression tolerance
   - [ ] Example evals for 2 Phase 1 skills
   - [ ] Target completion: ~5 days

3. **P0-02 Follow-up: Validation**
   - [ ] P0-02 design review with Phase 1 team
   - [ ] Confirm YAML serialization is implementable
   - [ ] Validate worked example covers all entity types
   - [ ] Lock schema version 1.0.0

### Week 2-3 of Phase 0 (Aug 24-Sep 6)

**Sequential start (depends on P0-02 lock):**

4. **P0-03: Staleness & Invalidation**
   - [ ] Dependency cascade algorithm
   - [ ] 5+ worked examples (ADR change, requirement clarification, code change, etc.)
   - [ ] Revalidation trigger policy
   - [ ] Target completion: ~6 days

5. **P0-04: Multi-Agent Consistency**
   - [ ] Conflict definition rules
   - [ ] Detection algorithm
   - [ ] Resolution protocol
   - [ ] Test matrix (5+ conflict scenarios)
   - [ ] Target completion: ~6 days

6. **P0-05: Resumability**
   - [ ] Reconstruction algorithm
   - [ ] Disambiguation rules
   - [ ] Handoff template
   - [ ] Worked example (mid-implementation break → resume)
   - [ ] Target completion: ~4 days

7. **P0-06: Rigor Profiles**
   - [ ] Lightweight / Standard / High-rigor artifact matrices
   - [ ] Selection criteria per profile
   - [ ] Mandatory-skill table per profile
   - [ ] 3 example projects (one per profile)
   - [ ] Target completion: ~5 days

8. **P0-08: Decision Escalation**
   - [ ] Map 8-step escalation behavior to context state
   - [ ] Define decision-required entity in context model
   - [ ] Workflow resumption protocol
   - [ ] Blocking policy + timeout rules
   - [ ] Worked example
   - [ ] Target completion: ~4 days

### Week 4 of Phase 0 (Sep 7-13)

9. **P0-09: Integrated Lifecycle Validation**
   - [ ] Run 6 representative scenarios through all 8 designs
   - [ ] Scenarios:
     1. Greenfield: vague idea → feature implemented → verified
     2. Brownfield: constrained API change with spike
     3. Interrupted: mid-work break → resume correctly
     4. Conflicts: concurrent agent updates → detected
     5. Stale: source changes → cascades propagate
     6. Lightweight: minimal artifacts → core goals achieved
   - [ ] Validate no design conflicts
   - [ ] Target completion: ~3 days

10. **Phase 0 Closure**
    - [ ] All workstreams reviewed by Phase 1 team
    - [ ] Phase 0 output documented + mapped to PRD sections
    - [ ] Risk register updated for Phase 1 dependencies
    - [ ] Phase 1 task board created
    - [ ] Phase 1 kickoff prep

---

## Phase 0 Deliverables

Each workstream produces:

```
P0-XX Design Document
├── Design Specification
│   ├── Rationale (why this design?)
│   ├── Decision table / algorithm / schema
│   ├── Constraints & assumptions
│   └── Future extensibility notes
│
├── Worked Examples (2-3 scenarios)
│   ├── Example 1: Happy path
│   ├── Example 2: Edge case / error handling
│   └── Example 3: Integration with other workstreams
│
├── Test Cases / Validation Scenarios
│   └── 3-5 test cases showing correct/incorrect behavior
│
└── Decision Log
    ├── Key decisions made
    ├── Alternatives considered
    └── Rationale for each decision
```

**Total:** 8 design documents + 1 validation report

---

## Success Criteria (Phase 0 Exit Gate)

### Completeness
- [ ] All 9 workstreams deliver design + examples + test cases
- [ ] All workstreams mapped to v0.2 PRD sections
- [ ] No PRD requirement left without corresponding P0 design

### Consistency
- [ ] P0-09 runs all 6 scenarios without design conflicts
- [ ] Dependencies between workstreams validated (e.g., routing → authority escalation → persistent state)
- [ ] No circular dependencies discovered

### Implementability
- [ ] Phase 1 team reviews all P0 designs; raises no conceptual blockers
- [ ] Phase 1 team can write Phase 1 task board based on P0 specs
- [ ] No "what does this mean?" questions left unanswered

### Risk Mitigation
- [ ] Phase 0 output reduces Phase 1 implementation risk from 60% to <20%
- [ ] Key decisions locked (YAML format, routing precedence, rigor profiles)
- [ ] Open decisions documented and deferred to Phase 1 if appropriate

---

## Team Composition & Roles

| Role | FTE | Duration | Responsibilities |
|---|---|---|---|
| Product/Architecture Lead | 1.0 | 4 weeks | Oversee all 9 workstreams; resolve design conflicts; validate consistency |
| Design Engineer #1 | 1.0 | 4 weeks | P0-01, P0-03, P0-04 (routing, staleness, multi-agent) |
| Design Engineer #2 | 1.0 | 4 weeks | P0-05, P0-06, P0-08 (resumability, profiles, escalation) |
| Eval/Quality Lead | 0.5 | 2 weeks | P0-07 (evaluation standard) |
| Tech Writer | 0.5 | 4 weeks | Document all workstreams; create worked examples |
| Phase 1 Reviewer | 0.25 | 2 weeks (weeks 3-4) | Review P0 designs before Phase 1 start |

**Total Effort:** ~10-12 FTE-weeks

---

## Communications & Synchronization

- **Weekly Sync:** All workstream owners + lead (Tuesday 10am)
- **Bi-weekly Review:** Phase 1 team reviews latest P0 outputs (alternate Fridays)
- **Decision Log:** Maintained in each P0 document
- **Risk Log:** Updated weekly
- **Dependency Check:** Every 3 days (ensure downstream work not blocked)

---

## Phase 1 Readiness Checklist

Before Phase 1 kickoff, confirm:

- [ ] All Phase 0 deliverables complete + reviewed
- [ ] P0-02 (Context schema) locked; Phase 1 can begin implementation
- [ ] P0-01 (Routing) locked; skill routing is unambiguous
- [ ] P0-07 (Eval standard) locked; Phase 1 knows quality bar
- [ ] P0-08 (Decision escalation) locked; skills know how to escalate
- [ ] P0-09 (Lifecycle validation) passes all 6 scenarios
- [ ] Phase 1 task board created from P0 designs
- [ ] No blocking questions from Phase 1 team
- [ ] Risk register reviewed; Phase 1 dependencies identified

---

## Key Decisions Made (Phase 0)

### Context Format (P0-02)
**Decision:** YAML is canonical authoritative format  
**Alternatives Considered:** JSON (verbose, no comments), SQLite (binary, not portable)  
**Rationale:** Human-readable, git-friendly, native support for nesting and comments  
**Status:** LOCKED  
**Date:** 2026-08-17

### No Parallel Representations (P0-02)
**Decision:** Single YAML source of truth; JSON export is optional and read-only  
**Rationale:** Prevents context.yaml ≠ context.json divergence; maintains truth integrity  
**Status:** LOCKED  
**Date:** 2026-08-17

---

## Open Decisions (For Phase 0 Team)

These will be decided during workstreams:

1. **Routing:** Should precedence tree be hardcoded or configurable per project?
2. **Multi-Agent:** Human escalation for all conflicts, or auto-resolution for specific cases?
3. **Profiles:** Can projects mix lightweight + standard + high-rigor (e.g., some work lightweight, some high-rigor)?
4. **Eval Scoring:** Weighted scoring (60% precision, 40% completeness) or pass/fail per dimension?
5. **Staleness:** Immediate invalidation or batch revalidation?

---

## Next Document

After P0-02 is locked, next: **P0-01: Routing & Precedence**

(To be created after Phase 0 team alignment)

---

**Prepared:** 2026-08-17  
**Next Review:** 2026-08-24  
**Phase 0 Start:** 2026-08-17  
**Phase 0 Target Completion:** 2026-09-13  
**Phase 1 Start:** 2026-09-16 (conditional on P0 pass gate)
