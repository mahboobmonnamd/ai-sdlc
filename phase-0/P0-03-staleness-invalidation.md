# P0-03: Staleness & Invalidation

**Workstream:** P0-03  
**Title:** Staleness Detection & Cascade Invalidation  
**Status:** Design Phase  
**Design Lead:** TBD (Design Engineer #1)  
**Start Date:** 2026-08-24  
**Target Completion:** 2026-08-30 (6 days)  
**Depends On:** P0-02 (Context Data Model) ✅, P0-01 (Routing States) ✅  

---

## Executive Summary

**Problem:** When a requirement changes, which downstream artifacts become invalid?
- Specification depends on requirement → should specification be marked stale?
- Implementation depends on specification → should it be marked stale?
- Tests depend on implementation → should tests be marked stale?
- **How do we automatically detect and cascade these invalidations?**

**Solution:** Staleness & Invalidation Model that:
1. Marks entities stale when upstream changes
2. Cascades invalidation through dependency chains
3. Determines what needs revalidation
4. Provides refresh strategy (immediate vs. batch)
5. Tracks invalidation history (audit trail)

**Outcome:** When context changes, system automatically identifies affected work (no manual "hunt for broken things").

---

## 1. Design Rationale

### Why Staleness Matters

**Without staleness tracking:**
```
Timeline:
├─ T0: FR-001 "User auth" (current)
│  └─ SPEC-087 "JWT implementation" (current)
│     └─ WI-042 "Implement JWT" (current)
│        └─ VER-199 "Test JWT" (current)
│
├─ T1: Someone updates FR-001 to "Support OAuth too"
│  └─ No one marks downstream as stale
│  └─ SPEC-087 still says "current" (WRONG)
│  └─ WI-042 proceeds with old spec
│  └─ VER-199 tests against wrong spec
│
├─ T2: Code review: "Why does JWT have OAuth support?"
│  └─ Investigation: "What changed?"
│  └─ Blame: "Who changed requirement?"
│  └─ Rework: Re-implement, re-test, re-verify
│  └─ Cost: Days of work, wasted effort
```

**With staleness tracking:**
```
Timeline:
├─ T0: FR-001 → SPEC-087 → WI-042 → VER-199 (all current)
│
├─ T1: FR-001 updated to "Support OAuth too"
│  └─ Staleness cascade fires automatically:
│     ├─ SPEC-087.validation_status = stale (FR-001 changed)
│     ├─ WI-042.validation_status = stale (SPEC-087 stale)
│     └─ VER-199.validation_status = stale (WI-042 stale)
│  └─ Routing triggered for each:
│     ├─ WI-042 → Gate 4: "artifact_stale" → Revalidate SPEC-087 first
│     └─ VER-199 → Gate 4: "artifact_stale" → Revalidate WI-042 first
│
├─ T2: Engineer revalidates SPEC-087
│  └─ "Oh, FR-001 now requires OAuth support"
│  └─ Updates SPEC-087 + WI-042 plan
│  └─ WI-042 can proceed with correct spec
```

### Design Constraints

1. **Automatic:** Cascade fires without manual "mark stale" commands
2. **Correct:** Staleness follows dependency graph (doesn't mark unrelated items)
3. **Traceable:** Audit trail shows what changed, when, why
4. **Performant:** Cascade detection doesn't require full graph traversal
5. **Configurable:** Different projects can use immediate vs. batch invalidation
6. **Reversible:** If change is reverted, can mark items as current again

---

## 2. Staleness State Machine

### State Definitions

```
Artifact Validation States:

┌─ current
│  └─ upstream entity changes
│     └─ → stale (OR needs_recheck depending on policy)
│
├─ stale
│  ├─ Someone revalidates artifact
│  │  └─ → current or conflicted
│  │
│  └─ Revalidation timeout expires (no action)
│     └─ → needs_recheck (escalate for manual review)
│
├─ needs_recheck
│  ├─ Someone revalidates + confirms
│  │  └─ → current
│  │
│  └─ Escalation approved
│     └─ → current or superseded
│
└─ conflicted
   ├─ Human resolves conflict
   │  └─ → current
   │
   └─ Change reverted
      └─ → current
```

### Validation Status Values

```yaml
validation_status:
  - current
      # Entity is valid; all upstream dependencies current
      # Routing: Can proceed past Gate 4
      # Action: None
  
  - stale
      # Upstream dependency changed; this entity may be outdated
      # Routing: Gate 4 fires → artifact_stale
      # Action: Revalidate and update if needed
  
  - needs_recheck
      # Stale entity wasn't revalidated within timeout
      # Routing: Gate 4 fires → artifact_stale (stronger alert)
      # Action: Manual review/escalation required
  
  - conflicted
      # Conflicting information detected
      # Example: Two upstream entities contradict each other
      # Example: Multi-agent concurrent updates created inconsistency
      # Routing: Gate 4 fires → requires authority resolution
      # Action: Resolve conflict before proceeding
```

---

## 3. Cascade Algorithm

### Invalidation Trigger

```python
def invalidate_entity(entity_id, context_model):
    """
    Entity changed → mark it current, cascade stale to downstream.
    """
    entity = context_model.get_artifact(entity_id)
    
    # Step 1: Mark entity as current (it was just updated/revalidated)
    entity.validation_status = "current"
    entity.last_validated = timestamp_now()
    entity.last_modified = timestamp_now()
    
    # Step 2: Find all entities that depend on this one
    downstream = context_model.find_by_relationship(
        depends_on_contains=entity_id,
        kind=any  # Any entity type
    )
    
    # Step 3: Cascade stale to downstream
    for downstream_entity in downstream:
        cascade_stale(downstream_entity, entity_id, context_model)


def cascade_stale(entity, invalidated_by, context_model, depth=0):
    """
    Recursively mark entity and its downstream as stale.
    """
    max_depth = 10  # Prevent infinite loops
    if depth > max_depth:
        log_warning(f"Cascade depth exceeded for {entity.id}")
        return
    
    # Don't re-cascade if already stale
    if entity.validation_status in ["stale", "needs_recheck", "conflicted"]:
        # Already stale; don't re-cascade (avoid redundant work)
        # But DO append to invalidated_by chain
        entity.invalidated_by.append(invalidated_by)
        return
    
    # Mark as stale
    entity.validation_status = "stale"
    entity.invalidated_by.append(invalidated_by)
    entity.cascade_timestamp = timestamp_now()
    
    # Cascade to all downstream of this entity
    downstream = context_model.find_by_relationship(
        depends_on_contains=entity.id
    )
    
    for downstream_entity in downstream:
        cascade_stale(downstream_entity, entity.id, context_model, depth + 1)
```

### Worked Example: ADR Change Cascades

```yaml
Initial State (all current):
├─ ADR-003: "Use JWT for authentication" (current)
│  └─ depends_on: []
│  └─ affects: [FR-001, FR-002, SPEC-002]
│
├─ FR-001: "User can log in" (current)
│  └─ depends_on: [ADR-003]
│
├─ FR-002: "Tokens expire after 1 hour" (current)
│  └─ depends_on: [ADR-003]
│
├─ SPEC-002: "JWT implementation spec" (current)
│  └─ depends_on: [FR-001, FR-002]
│  └─ affects: [WI-042]
│
└─ WI-042: "Implement JWT auth" (current)
   └─ depends_on: [SPEC-002]
   └─ affects: [VER-087]

Event: ADR-003 changed to "Use Session tokens instead of JWT"

Step 1: invalidate_entity(ADR-003, context)
├─ ADR-003.validation_status = current (it was just updated)
├─ Find downstream: [FR-001, FR-002, SPEC-002] (from affects list)
└─ Call cascade_stale() for each

Step 2: cascade_stale(FR-001, ADR-003, depth=0)
├─ FR-001.validation_status = stale
├─ FR-001.invalidated_by = [ADR-003]
├─ Find downstream: [SPEC-002] (depends_on FR-001)
└─ Call cascade_stale(SPEC-002, FR-001, depth=1)

Step 3: cascade_stale(SPEC-002, FR-001, depth=1)
├─ SPEC-002.validation_status = stale
├─ SPEC-002.invalidated_by = [ADR-003, FR-001]
├─ Find downstream: [WI-042] (depends_on SPEC-002)
└─ Call cascade_stale(WI-042, SPEC-002, depth=2)

Step 4: cascade_stale(WI-042, SPEC-002, depth=2)
├─ WI-042.validation_status = stale
├─ WI-042.invalidated_by = [ADR-003, FR-001, SPEC-002]
├─ Find downstream: [VER-087] (depends_on WI-042)
└─ Call cascade_stale(VER-087, SPEC-002, depth=3)

Step 5: cascade_stale(VER-087, SPEC-002, depth=3)
├─ VER-087.validation_status = stale
├─ VER-087.invalidated_by = [ADR-003, FR-001, SPEC-002, WI-042]
└─ No downstream → cascade complete

Final State:
├─ ADR-003: current ✅ (just updated)
├─ FR-001: stale ❌ (ADR-003 changed)
├─ FR-002: stale ❌ (ADR-003 changed)
├─ SPEC-002: stale ❌ (FR-001, FR-002 changed)
├─ WI-042: stale ❌ (SPEC-002 changed)
└─ VER-087: stale ❌ (WI-042 changed)

Audit Trail:
├─ ADR-003.last_modified = 2026-08-24T14:30:00Z
├─ FR-001.invalidated_by = [ADR-003]
├─ SPEC-002.invalidated_by = [ADR-003, FR-001]
├─ WI-042.invalidated_by = [ADR-003, FR-001, SPEC-002]
└─ VER-087.invalidated_by = [ADR-003, FR-001, SPEC-002, WI-042]

Routing Impacts:
├─ FR-001: Gate 4 → artifact_stale (needs revalidation)
├─ SPEC-002: Gate 4 → artifact_stale (needs revalidation)
├─ WI-042: Gate 4 → artifact_stale (routing blocked)
└─ VER-087: Gate 4 → artifact_stale (routing blocked)
```

---

## 4. Revalidation Strategy

### Revalidation Trigger Points

```yaml
When to Revalidate:

Policy 1: Immediate (Strict)
├─ On upstream change: Immediately mark stale
├─ On routing: Block at Gate 4, force revalidation
├─ Best for: High-rigor projects, critical paths
├─ Cost: More revalidation work, less batching

Policy 2: Batch (Relaxed)
├─ On upstream change: Mark stale but don't block
├─ At end of day: Batch revalidation of stale artifacts
├─ Best for: Fast-moving projects, high churn
├─ Cost: Stale artifacts in flight longer, but fewer interruptions

Policy 3: Timeout (Hybrid)
├─ On upstream change: Mark stale
├─ After N hours: If not revalidated, mark needs_recheck
├─ On routing: Block at Gate 4
├─ Best for: Mixed-priority work
```

### Revalidation Decision Tree

```python
def should_revalidate(entity, context_model):
    """
    Decide if entity needs revalidation or can proceed as-is.
    """
    if entity.validation_status == "current":
        return False  # Already valid
    
    if entity.validation_status == "needs_recheck":
        return True  # Timeout expired; must revalidate
    
    if entity.validation_status == "stale":
        revalidation_policy = context_model.get_project_config("staleness_policy")
        
        if revalidation_policy == "immediate":
            return True  # Immediate revalidation
        
        elif revalidation_policy == "batch":
            # Check if in batch window (e.g., end of day)
            time_since_stale = now() - entity.cascade_timestamp
            batch_window = 24 * 3600  # 24 hours
            return time_since_stale > batch_window
        
        elif revalidation_policy == "timeout":
            time_since_stale = now() - entity.cascade_timestamp
            timeout = 4 * 3600  # 4 hours
            if time_since_stale > timeout:
                entity.validation_status = "needs_recheck"
                return True
            else:
                return False
    
    if entity.validation_status == "conflicted":
        return "escalate"  # Requires human resolution


def revalidate_entity(entity, context_model):
    """
    Revalidate entity against upstream dependencies.
    """
    # Step 1: Get upstream dependencies
    upstream_ids = entity.depends_on
    upstream_entities = [context_model.get_artifact(id) for id in upstream_ids]
    
    # Step 2: Check if upstream are all current
    stale_upstream = [u for u in upstream_entities if u.validation_status != "current"]
    
    if stale_upstream:
        # Upstream not ready yet; stay stale
        log_info(f"{entity.id}: Upstream not ready; staying stale")
        return {
            "action": "blocked",
            "reason": f"Upstream {[u.id for u in stale_upstream]} still stale"
        }
    
    # Step 3: Revalidate entity content
    invalidated_by_chain = entity.invalidated_by
    upstream_changes = {
        upstream.id: {
            "old_value": context_model.get_artifact_history(upstream.id, -1),
            "new_value": upstream
        }
        for upstream in upstream_entities
    }
    
    # Step 4: Check for conflicts in changes
    conflicts = detect_conflicts(entity, upstream_changes, context_model)
    
    if conflicts:
        entity.validation_status = "conflicted"
        entity.conflict_details = conflicts
        return {
            "action": "escalate",
            "reason": f"Conflicts detected: {conflicts}"
        }
    
    # Step 5: Update entity with changes (if needed)
    changes_needed = determine_entity_changes(entity, upstream_changes, context_model)
    
    if changes_needed:
        apply_changes(entity, changes_needed)
        entity.validation_status = "current"
        entity.last_validated = timestamp_now()
        return {
            "action": "updated",
            "reason": f"Revalidated and updated: {changes_needed}"
        }
    else:
        entity.validation_status = "current"
        entity.last_validated = timestamp_now()
        return {
            "action": "confirmed",
            "reason": "Revalidated; no changes needed"
        }
```

---

## 5. Conflict Detection in Revalidation

### Conflict Types

```yaml
Type 1: Direct Contradiction
├─ Example: FR-001 says "Support OAuth" but FR-002 says "No external auth"
├─ Detection: Check for contradicts relationships
├─ Resolution: Authority resolves which requirement is correct

Type 2: Incompatible Upstream Changes
├─ Example: API spec changed (breaking), impl still assumes old API
├─ Detection: Revalidate found breaking changes
├─ Resolution: Update implementation or negotiate API compatibility

Type 3: Multi-Agent Conflict
├─ Example: Skill A updated SPEC-001 to "Use REST"; Skill B to "Use GraphQL"
├─ Detection: Last-write-wins would lose Skill A's change
├─ Resolution: P0-04 (Multi-Agent) handles this; escalate here

Type 4: Inconsistent Cascade
├─ Example: SPEC-002 depends on FR-001 and FR-002; only one changed
├─ Detection: Check if changes are consistent across all dependents
├─ Resolution: Usually not a conflict; just partial update
```

---

## 6. Invalidation Metadata

### New Fields in Context Schema

```yaml
artifact:
  # ... existing fields ...
  
  validation_status:
    type: enum [current, stale, needs_recheck, conflicted]
    description: "Current validity status"
  
  last_validated:
    type: timestamp
    description: "Last time this artifact was confirmed valid"
    example: "2026-08-23T10:30:00Z"
  
  invalidated_by:
    type: list[entity_id]
    description: "Chain of upstream changes that made this stale"
    example: ["ADR-003", "FR-001", "SPEC-002"]
    order: "Most recent first"
  
  cascade_timestamp:
    type: timestamp
    description: "When this entity was marked stale (cascade fired)"
    example: "2026-08-24T14:30:00Z"
  
  revalidation_status:
    type: enum [pending, in_progress, complete]
    description: "Is revalidation currently happening?"
  
  conflict_details:
    type: object
    description: "If validation_status=conflicted, what's the conflict?"
    fields:
      conflict_type: enum [contradiction, incompatible_changes, multi_agent, other]
      affected_fields: [list of field names]
      upstream_versions: {entity_id: version}
      resolution_required: bool
      escalation_id: string (links to decision_escalation)
```

---

## 7. Performance Optimization

### Cascade Optimization

```python
# Naive approach (too slow):
# For every changed entity, walk entire dependency graph

# Optimization 1: Use affects + depends_on indices
# Context model maintains:
#   - depends_on_index: {entity_id: [downstream_ids]}
#   - affected_by_index: {entity_id: [upstream_ids]}
# Cascade lookup: O(1) per entity, not O(n)

# Optimization 2: Stop at already-stale entities
# Don't re-cascade through entities that are already stale
# (They're already marked and already propagating staleness)

# Optimization 3: Batch changes
# Don't run cascade for each individual change
# Batch all changes in a transaction → single cascade run
# Reduces redundant marking of same entities

# Example:
# Change 1: FR-001 updated
# Change 2: FR-002 updated
# (both go to SPEC-002)
# 
# Naive: SPEC-002 marked stale twice
# Batched: SPEC-002 marked stale once, both FR-001 and FR-002 in invalidated_by

def invalidate_batch(entity_ids, context_model):
    """
    Cascade for multiple changed entities in one operation.
    """
    # Step 1: Mark all changed entities as current
    for entity_id in entity_ids:
        context_model.get_artifact(entity_id).validation_status = "current"
    
    # Step 2: Collect all downstream (union, deduplicated)
    all_downstream = set()
    for entity_id in entity_ids:
        downstream = context_model.find_by_relationship(
            depends_on_contains=entity_id
        )
        all_downstream.update(downstream)
    
    # Step 3: Single cascade run for all downstream
    for entity in all_downstream:
        # Determine which upstream entities invalidated this one
        invalidators = [
            entity_id for entity_id in entity_ids
            if entity_id in entity.depends_on
        ]
        cascade_stale(entity, invalidators, context_model)
```

---

## 8. Acceptance Criteria

Staleness implementation is complete when:

- [ ] **AC-1:** Invalidation cascade algorithm implemented (recursive marking)
- [ ] **AC-2:** Cascade deterministic + auditable (invalidated_by chain)
- [ ] **AC-3:** Staleness state machine handles all 4 states + transitions
- [ ] **AC-4:** Revalidation decision tree implemented (immediate/batch/timeout policies)
- [ ] **AC-5:** Conflict detection identifies 4+ conflict types
- [ ] **AC-6:** Integration with P0-01 routing: Gate 4 correctly routes on staleness
- [ ] **AC-7:** Integration with P0-02 context schema: all staleness metadata stored
- [ ] **AC-8:** Batch invalidation supported (multiple changes → single cascade)
- [ ] **AC-9:** Worked examples trace cascade through 5+ levels (ADR → SPEC → WI → VER)
- [ ] **AC-10:** Performance acceptable (cascade < 100ms for 100-entity graph)

---

## 9. Decision Log

### Decision: Cascade Direction (Push vs. Pull)

**Decision:** Cascade uses PUSH model (mark downstream stale).

**Alternatives:**
1. **Push Model (chosen):** When X changes, mark all downstream as stale
   - Pro: Catch problems early; downstream knows it's stale
   - Con: More upfront work

2. **Pull Model:** When X asked "are you valid?", walk up dependencies
   - Pro: Only check when needed
   - Con: Latency at evaluation time; repeated checks

**Rationale:** Staleness should be immediately visible. Downstream should know without asking.

**Status:** LOCKED  
**Date:** 2026-08-24

---

### Decision: Invalidation Policy Default (Immediate)

**Decision:** Default policy = immediate (mark stale right away; block on routing).

**Rationale:** Safety first. Stale artifacts are visible early. Projects can opt-in to batch for performance.

**Status:** PENDING  
**Date:** TBD (Phase 1 projects decide)

---

### Decision: Invalidated_by Chain (Keep Full History)

**Decision:** Store full chain: SPEC-002.invalidated_by = [ADR-003, FR-001]

**Alternatives:**
1. Keep full chain (chosen) — Full audit trail
2. Keep only direct cause (SPEC-002.invalidated_by = [FR-001]) — Simpler
3. Keep only root cause (SPEC-002.invalidated_by = [ADR-003]) — Most direct

**Rationale:** Tracing full cascade helps understand what happened. "SPEC depends on FR which depends on ADR which changed."

**Status:** LOCKED  
**Date:** 2026-08-24

---

## 10. Open Questions

1. **Should cascade be automatic or manual trigger?** (Current: automatic on every change)
2. **What's the timeout for needs_recheck escalation?** (4h? 24h? Project config?)
3. **Should conflicts trigger decision_escalation automatically?** (Or wait for manual escalation?)
4. **Can entities opt-out of cascading?** (E.g., "this change doesn't affect downstream")
5. **Should cascade respect rigor profile?** (High-rigor: strict; lightweight: relaxed?)

---

## 11. Integration Points

### With P0-01 (Routing)
- Gate 4: "Is artifact stale?" → Calls this module to check validation_status
- Gate 4: "artifact_stale" state → Directs to revalidation workflow

### With P0-02 (Context Schema)
- Staleness metadata: validation_status, invalidated_by, cascade_timestamp, conflict_details
- Relationship types: depends_on, affects (drive cascade graph)

### With P0-04 (Multi-Agent)
- Multi-agent conflict: Two skills update same artifact → conflicted state
- Conflict detection: Use this module's conflict logic

### With P0-05 (Resumability)
- Session resume: Reconstruct cascade from invalidated_by chain
- Know what needs revalidation without replaying entire history

---

## 12. Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-24 | Cascade algorithm + state machine | TBD | In progress |
| 2026-08-25 | Revalidation strategy + conflict detection | TBD | Not started |
| 2026-08-26 | Integration with routing (P0-01) | TBD | Not started |
| 2026-08-27 | Worked examples (5+ levels) + test cases | TBD | Not started |
| 2026-08-28 | Performance optimization + acceptance review | TBD | Not started |
| 2026-08-30 | Design complete + ready for P0-04 | TBD | Not started |

---

**P0-03 Design: Staleness & Invalidation — READY FOR TEAM EXECUTION**

Next: Assign Design Engineer #1 to complete by 2026-08-30.

Then: P0-04 (Multi-Agent Consistency) depends on staleness model.
