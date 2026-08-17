# P0-04: Multi-Agent Consistency

**Workstream:** P0-04  
**Title:** Multi-Agent Consistency: Detecting Conflicts When Multiple Skills Work in Parallel  
**Status:** Design Phase  
**Design Lead:** TBD (Design Engineer #2)  
**Start Date:** 2026-08-24  
**Target Completion:** 2026-08-30 (6 days)  
**Depends On:** P0-01 (Routing states) ✅, P0-03 (Staleness cascade) ⏳ (Aug 30)  

---

## Executive Summary

**Problem:** When multiple skills run in parallel on the same project:
- Skill A writes: "Use JWT for auth"
- Skill B writes: "Use OAuth for auth"
- Result: Conflicted context; unclear which is correct

**Solution:** Define conflict detection mechanism that:
1. Detects when multiple agents update the same artifact
2. Identifies conflicting changes (contradictions, incompatible implementations)
3. Routes conflicts to decision escalation (P0-08)
4. Prevents silent overwrite of each other's changes
5. Ensures consistency before proceeding

**Outcome:** Multi-agent work is safe. Conflicts are detected early and escalated for resolution.

---

## 1. Design Rationale

### Why Multi-Agent Consistency Matters

**Without conflict detection:**
```
Skill A (Requirement Analyzer): "Auth must use JWT"
Skill B (Spec Writer): "Auth will use OAuth"
Skill C (Implementer): "Implementing OAuth"
Skill D (Tester): "Testing JWT integration"
→ No conflict detected
→ Implementation uses OAuth, tests fail with JWT
→ Production broken
```

**With conflict detection:**
```
Skill A writes: "Use JWT"
Skill B tries to write: "Use OAuth"
Conflict detector fires: "Contradiction detected"
Created: decision_escalation ESCA-001
Routing blocks B: "awaiting_decision"
Authority decides: "Use JWT"
Skill B updates spec for JWT
All skills proceed in sync
```

### Design Constraints

1. **Deterministic:** Same conflict scenario → same detection
2. **Non-Destructive:** Never silently overwrite; always escalate on conflict
3. **Fine-Grained:** Detect conflicts at field level (not just entity level)
4. **Audit-Able:** Record what conflicted, who changed what, when
5. **Resumable:** After conflict resolved, retrying original operation should work
6. **Performance:** O(1) or O(log n) conflict check (not O(n²))

---

## 2. Conflict Detection Types

### Type 1: Direct Contradiction

**Scenario:** Two skills update the same field with different values

```yaml
Artifact: FR-001 (Functional Requirement)

Change 1 (Skill A - Req Analyzer):
  field: authentication_mechanism
  new_value: JWT
  timestamp: 2026-08-24T10:00:00Z

Change 2 (Skill B - Spec Writer):
  field: authentication_mechanism
  new_value: OAuth
  timestamp: 2026-08-24T10:05:00Z

Conflict Detection:
  type: direct_contradiction
  artifact_id: FR-001
  field: authentication_mechanism
  value_1: JWT (by Skill A)
  value_2: OAuth (by Skill B)
  timestamp_1: 2026-08-24T10:00:00Z
  timestamp_2: 2026-08-24T10:05:00Z
  severity: HIGH (contradictory implementations)
```

### Type 2: Incompatible Changes

**Scenario:** Two skills make changes that are technically incompatible

```yaml
Artifact: SPEC-087 (Authentication Specification)

Change 1 (Skill A):
  section: authentication_flow
  adds: "OAuth 2.0 with Auth0 provider"
  timestamp: 2026-08-24T10:00:00Z

Change 2 (Skill B):
  section: infrastructure
  specifies: "No third-party dependencies"
  timestamp: 2026-08-24T10:05:00Z

Conflict Detection:
  type: incompatible_changes
  artifact_id: SPEC-087
  conflict_between: [authentication_flow, infrastructure]
  incompatibility: "Auth0 (third-party) contradicts 'no third-party dependencies'"
  severity: HIGH
  recommendation: "Escalate to architecture review"
```

### Type 3: Multi-Agent Race Condition

**Scenario:** Same skill tries to update artifact being modified by another skill

```yaml
State Before:
  FR-001:
    acceptance_criteria: ["User can log in"]
    version: 1

Skill A starts reading FR-001 (version 1): 2026-08-24T10:00:00Z
Skill B updates FR-001: 2026-08-24T10:01:00Z
  new version: 2
  added_criteria: ["User can reset password"]

Skill A tries to update FR-001 (based on version 1): 2026-08-24T10:02:00Z
  adds_criteria: ["User can log out"]

Conflict Detection:
  type: race_condition
  artifact_id: FR-001
  reader_version: 1
  current_version: 2
  changes_missed: ["User can reset password"]
  attempted_change: "Add: User can log out"
  severity: MEDIUM (data loss risk)
  action: Reject update; notify skill to re-read and retry
```

### Type 4: Indirect Conflict (via Dependencies)

**Scenario:** Two skills make changes to different artifacts that have a dependency conflict

```yaml
Change 1 (Skill A):
  Artifact: ADR-003
  change: "Use JWT for auth"
  timestamp: 2026-08-24T10:00:00Z

Change 2 (Skill B):
  Artifact: FR-001
  change: "Support social login with OAuth"
  timestamp: 2026-08-24T10:05:00Z

Conflict Detection:
  type: indirect_conflict (via cascade)
  conflict_between: [ADR-003, FR-001]
  relationship: ADR-003 affects FR-001
  issue: "ADR-003 = JWT (doesn't support social), FR-001 requires social login"
  severity: HIGH (cascades down to SPEC, WI, VER)
  cascade_impact: [SPEC-087, WI-042, VER-087]
  action: Mark ADR-003 and FR-001 as conflicted; escalate
```

---

## 3. Conflict Detection Algorithm

### Core Logic: Check Before Write

```python
def detect_conflicts_on_write(artifact_id, proposed_changes, context_model):
    """
    Before any skill writes to artifact, check for conflicts.
    Returns: conflict_report (empty if no conflicts, non-empty if conflicts)
    """
    artifact = context_model.get_artifact(artifact_id)
    
    # Type 1: Direct Contradiction
    direct_conflicts = check_direct_contradiction(
        artifact=artifact,
        proposed_changes=proposed_changes
    )
    if direct_conflicts:
        return {
            "conflicts_detected": True,
            "type": "direct_contradiction",
            "details": direct_conflicts,
            "action_required": "escalate_decision"
        }
    
    # Type 2: Incompatible Changes
    incompatible = check_incompatible_changes(
        artifact=artifact,
        proposed_changes=proposed_changes
    )
    if incompatible:
        return {
            "conflicts_detected": True,
            "type": "incompatible_changes",
            "details": incompatible,
            "action_required": "escalate_decision"
        }
    
    # Type 3: Race Condition (version mismatch)
    race_condition = check_version_match(
        artifact=artifact,
        reader_version=proposed_changes.get("artifact_version")
    )
    if race_condition:
        return {
            "conflicts_detected": True,
            "type": "race_condition",
            "details": race_condition,
            "action_required": "retry_after_reread"
        }
    
    # Type 4: Indirect Conflict (downstream impact)
    indirect = check_downstream_conflicts(
        artifact=artifact,
        proposed_changes=proposed_changes,
        context_model=context_model
    )
    if indirect:
        return {
            "conflicts_detected": True,
            "type": "indirect_conflict",
            "details": indirect,
            "action_required": "escalate_decision",
            "cascade_impact": indirect.get("affected_artifacts")
        }
    
    # No conflicts
    return {"conflicts_detected": False}


def check_direct_contradiction(artifact, proposed_changes):
    """
    Check if proposed change contradicts existing value in same field.
    """
    conflicts = []
    
    for field, new_value in proposed_changes.items():
        current_value = artifact.get(field)
        
        if current_value is not None and current_value != new_value:
            # Check if contradiction (not just update)
            is_contradiction = are_mutually_exclusive(current_value, new_value)
            if is_contradiction:
                conflicts.append({
                    "field": field,
                    "current_value": current_value,
                    "proposed_value": new_value,
                    "severity": "HIGH",
                    "reason": "Mutually exclusive values"
                })
    
    return conflicts if conflicts else None


def check_incompatible_changes(artifact, proposed_changes):
    """
    Check if proposed changes create incompatibilities with existing sections.
    """
    # For each proposed change, check against all existing sections
    incompatibilities = []
    
    for section, content in proposed_changes.items():
        for existing_section, existing_content in artifact.items():
            if section != existing_section:
                # Check if new section contradicts existing section
                if is_incompatible(content, existing_content):
                    incompatibilities.append({
                        "new_section": section,
                        "new_content": content,
                        "conflicting_section": existing_section,
                        "conflicting_content": existing_content,
                        "reason": f"{section} contradicts {existing_section}"
                    })
    
    return incompatibilities if incompatibilities else None


def check_version_match(artifact, reader_version):
    """
    Check if reader is operating on latest version.
    Prevents silent data loss in race conditions.
    """
    current_version = artifact.get("version", 1)
    
    if reader_version and reader_version < current_version:
        changes_made = artifact.get("changes_since_version", {}).get(reader_version, [])
        return {
            "reader_version": reader_version,
            "current_version": current_version,
            "changes_missed": changes_made,
            "severity": "MEDIUM",
            "reason": "Data loss risk; artifact modified since read"
        }
    
    return None


def check_downstream_conflicts(artifact, proposed_changes, context_model):
    """
    Check if proposed change creates conflicts downstream via dependencies.
    """
    # Get all artifacts that depend on this one
    dependent_artifacts = context_model.find_by_relationship(
        kind="*",
        depends_on=artifact.id
    )
    
    conflicts = []
    for dependent in dependent_artifacts:
        for field, new_value in proposed_changes.items():
            # Check if dependent has contradictory requirement
            if conflicts_with_dependent(new_value, dependent):
                conflicts.append({
                    "artifact_id": artifact.id,
                    "proposed_change": {field: new_value},
                    "dependent_artifact": dependent.id,
                    "dependent_requirement": dependent.get_requirement_for_field(field),
                    "cascade_impact": "dependent becomes conflicted",
                    "severity": "HIGH"
                })
    
    return conflicts if conflicts else None
```

---

## 4. Conflict Resolution Path

### When Conflict Detected: Three Options

```
┌─ Conflict Detected ─┐
│                     │
├─ Type 1/2/4: Direct/Indirect/Incompatible
│  └─ Escalate to Decision (P0-08)
│     └─ Authority decides which change to keep
│
├─ Type 3: Race Condition
│  └─ Skill retries (re-reads, merges, updates)
│
└─ No Conflict
   └─ Write allowed
```

### Escalation Path (Type 1/2/4)

```python
def escalate_conflict_to_decision(
    artifact_id, 
    conflict_report, 
    context_model
):
    """
    Create decision_escalation for conflicted change.
    """
    
    # Option 1: Keep existing value
    option_1 = {
        "id": "OPT-KEEP",
        "name": f"Keep existing: {conflict_report['current_value']}",
        "description": "Proceed with what's currently documented",
        "pros": ["Avoids disruption", "Coherent with downstream"],
        "cons": ["Ignores new insight", "May miss requirement"]
    }
    
    # Option 2: Accept proposed change
    option_2 = {
        "id": "OPT-NEW",
        "name": f"Accept new: {conflict_report['proposed_value']}",
        "description": "Override with new value",
        "pros": ["Latest thinking", "May be more correct"],
        "cons": ["Requires rework downstream", "May break dependent"]
    }
    
    # Option 3: Merge or rethink
    option_3 = {
        "id": "OPT-MERGE",
        "name": "Merge or rethink",
        "description": "Are both partially correct? Can we synthesize?",
        "pros": ["Best of both", "Creative solution"],
        "cons": ["Requires deep thought", "May not be possible"]
    }
    
    # Create escalation
    escalation = create_decision_escalation(
        decision_topic=f"Resolve conflict on {artifact_id}.{conflict_report['field']}",
        blocking_work_item=artifact_id,
        options=[option_1, option_2, option_3],
        context=conflict_report,
        authority_required="tech_lead"  # or product_lead depending on type
    )
    
    return escalation
```

### Retry Path (Type 3: Race Condition)

```python
def retry_after_race_condition(
    artifact_id,
    conflict_report,
    skill_context
):
    """
    Skill should retry: re-read, check what changed, merge if needed.
    """
    
    # Notify skill of conflict
    skill_context.notify(
        message=f"Conflict: {conflict_report['reason']}",
        action="retry",
        details=conflict_report
    )
    
    # Skill retries:
    # 1. Re-read artifact (gets latest version)
    # 2. Check what changed since original read
    # 3. Merge if possible, or escalate if incompatible
    
    return {"action": "retry"}
```

---

## 5. Conflict Entity (P0-02 Context Schema Addition)

### New Entity Kind: conflict

```yaml
conflict:
  kind: "conflict"
  
  # Identity
  id: string (CONF-001)
  created_at: timestamp
  detected_by: string (skill_id)
  
  # Conflict Details
  type: enum (direct_contradiction, incompatible_changes, race_condition, indirect_conflict)
  artifact_ids: [list] (which artifacts conflicted)
  
  # Specific to type
  
  # Type 1: direct_contradiction
  field: string (field_name)
  current_value: any
  proposed_value: any
  
  # Type 2: incompatible_changes
  conflicting_sections: [list] ({section_name, content})
  incompatibility_reason: string
  
  # Type 3: race_condition
  reader_version: number
  current_version: number
  changes_missed: [list]
  
  # Type 4: indirect_conflict
  cascade_impact: [list] (affected artifact IDs)
  dependency_chain: [list] (ADR-003 → FR-001 → SPEC-087)
  
  # Resolution
  status: enum (detected, escalated, resolved, retry_requested)
  escalation_id: string (ESCA-001, if escalated)
  resolution: string (what was decided)
  resolved_at: timestamp
  
  # Audit
  affected_skills: [list] (Skill A, Skill B)
  timestamp_skill_a_change: timestamp
  timestamp_skill_b_change: timestamp
  time_to_detection_ms: number
```

---

## 6. Integration Points

### Integration with P0-01 (Routing)

When conflict detected, artifact enters conflicted validation_status.

```yaml
routing_state:
  artifact: FR-001
  validation_status: conflicted  # New status
  routing_decision: awaiting_decision  # Gate 1 fires
  escalation_id: ESCA-001  # Links to conflict escalation
```

### Integration with P0-03 (Staleness)

When conflict resolved, may trigger cascade invalidation if change was significant.

```yaml
conflict_resolution: "Changed from JWT to OAuth"

Cascade:
  FR-001 changed → SPEC-087 stale → WI-042 stale → VER-087 stale
```

### Integration with P0-08 (Escalation)

Conflicts create decision_escalation entities for resolution.

---

## 7. Acceptance Criteria

Multi-Agent Consistency implementation is complete when:

- [ ] **AC-1:** Four conflict types defined and detectable (direct, incompatible, race, indirect)
- [ ] **AC-2:** Conflict detection algorithm with check-before-write
- [ ] **AC-3:** Conflict entity schema defined
- [ ] **AC-4:** Direct/incompatible/indirect conflicts → decision escalation
- [ ] **AC-5:** Race condition conflicts → retry with merge
- [ ] **AC-6:** Integration with routing (conflicted validation_status)
- [ ] **AC-7:** Integration with staleness (cascade when resolved)
- [ ] **AC-8:** Worked examples (2-3 multi-skill scenarios)
- [ ] **AC-9:** Performance < 100ms for conflict detection
- [ ] **AC-10:** Audit trail (which skills conflicted, when, resolution)

---

## 8. Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-24 | 4 conflict types + detection algorithm | TBD | In progress |
| 2026-08-25 | Conflict entity schema + race condition retry | TBD | Not started |
| 2026-08-26 | Integration with P0-01 routing | TBD | Not started |
| 2026-08-27 | Integration with P0-08 escalation | TBD | Not started |
| 2026-08-28 | Worked examples + performance testing | TBD | Not started |
| 2026-08-30 | Design complete + ready for P0-09 | TBD | Not started |

---

**P0-04 Design: Multi-Agent Consistency — READY FOR TEAM EXECUTION**

Next: Assign Design Engineer #2 to complete by 2026-08-30.
