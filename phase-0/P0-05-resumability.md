# P0-05: Resumability

**Workstream:** P0-05  
**Title:** Resumability: Reconstructing Work State After Interruption  
**Status:** Design Phase  
**Design Lead:** TBD (Design Engineer #2)  
**Start Date:** 2026-08-24  
**Target Completion:** 2026-08-28 (4 days)  
**Depends On:** P0-01 (Routing states) ✅, P0-03 (Staleness cascade) ⏳ (Aug 30)  

---

## Executive Summary

**Problem:** Skills run long workflows (hours or days). When interrupted (user cancels, crash, timeout):
- "What was I doing?"
- "Where do I resume?"
- "Did anything change while I was working?"
- "What state is the work in?"

**Solution:** Define resumability model that:
1. Records checkpoints (work-in-progress state)
2. Persists unfinished work to durable storage
3. Detects changes while paused (external updates)
4. Reconstructs work state on resume
5. Decides: continue, restart, or escalate

**Outcome:** Long-running skills can survive interruption. Work is never lost.

---

## 1. Design Rationale

### Why Resumability Matters

**Without resumability:**
```
Skill: "Analyze requirements" (running 4 hours)
After 2 hours: User closes laptop / network drops / timeout
Skill state: Lost
On resume: Skill re-reads requirements (might have changed)
Result: 2 hours of work lost; might conflict with changes
```

**With resumability:**
```
Skill: "Analyze requirements" (running 4 hours)
Every 5 min: Checkpoint saved to durable storage
  Checkpoint contains: Current analysis, what's left, dependencies
After 2 hours: Interrupted
On resume: Skill reads checkpoint (2-hour mark)
  Checks if requirements changed (via invalidated_by chain)
  If no changes: Resume from checkpoint
  If changes: Re-analyze changed requirement
Result: 2 hours of work preserved; safe to continue
```

### Design Constraints

1. **Durable:** Checkpoint survives process crash, power loss, network failure
2. **Efficient:** Checkpointing doesn't add > 10% overhead
3. **Correct:** Detects if upstream changed; decides: resume or restart
4. **Atomic:** Checkpoint writes are atomic (all-or-nothing)
5. **Queryable:** Can ask "where would I resume?" without executing
6. **Bounded:** Checkpoints don't grow unbounded (old ones cleaned up)

---

## 2. Checkpoint Model

### What Gets Checkpointed?

```yaml
checkpoint:
  # Identity
  id: string (CP-001)
  skill_id: string (requirement_analyzer_v2)
  created_at: timestamp
  checkpoint_sequence: number (1, 2, 3...)
  
  # Work State
  work_item_id: string (WI-042)
  phase: string (requirements | design | implementation | verification)
  stage: string (in_progress value, e.g., "analyzing_fr_001")
  
  # Artifacts Being Worked On
  current_artifact: {
    id: string (FR-001)
    kind: string (requirement)
    version: number (42)
    validation_status: string (current)
  }
  
  # Progress Tracking
  items_processed: number (3 of 10 requirements analyzed)
  items_total: number (10)
  completion_percent: number (30%)
  
  # Work Results (What's been done so far)
  intermediate_results: {
    analyzed_requirements: [FR-001, FR-002, FR-003]
    pending_requirements: [FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010]
    issues_found: [
      {id: "issue-1", type: "ambiguous", artifact: FR-002, description: "..."}
    ]
    decisions_needed: [
      {topic: "Scope of FR-003", required_for: "continue"}
    ]
  }
  
  # Dependencies & Validation
  depends_on: [FR-001, FR-002, FR-003]  # What was read
  affects: [SPEC-087, WI-042]  # What will be affected
  
  # Staleness Detection
  upstream_versions: {
    FR-001: {version_at_read: 5, current_version: 5},
    FR-002: {version_at_read: 3, current_version: 3},
    FR-003: {version_at_read: 7, current_version: 8}  # Changed!
  }
  
  # Storage
  checkpoint_data: blob (serialized work state)
  checkpoint_size_bytes: number
  storage_location: string (s3://bucket/cp-001)
  
  # Lifecycle
  status: enum (active, superseded, cleaned_up)
  parent_checkpoint: string (CP-000, if this is a retry)
```

### Checkpoint Timing

```
Skill: "Analyze requirements"
├─ T=0s: Start
├─ T=30s: Process FR-001 → CP-001 created
├─ T=60s: Process FR-002 → CP-002 created
├─ T=90s: INTERRUPTED
│
├─ [Later, resume]
├─ T=91s: Checkpoint CP-002 loaded
├─ T=92s: Check if FR-001, FR-002 still current
├─ T=93s: Detect FR-003 changed (version 7→8)
├─ T=94s: Decide: Resume or restart
├─ T=95s+: Resume from CP-002 (with awareness of FR-003 change)
```

---

## 3. Resumability Workflow

### Step 1: Detect Interruption

```python
def detect_interruption(skill_id, context_model):
    """
    Check if skill has active checkpoint (was interrupted).
    """
    active_checkpoints = context_model.find_by_filter(
        kind="checkpoint",
        skill_id=skill_id,
        status="active"
    )
    
    if active_checkpoints:
        latest_checkpoint = active_checkpoints[-1]  # Most recent
        return {
            "interrupted": True,
            "checkpoint_id": latest_checkpoint.id,
            "last_checkpoint_time": latest_checkpoint.created_at,
            "time_since_checkpoint": time_elapsed(latest_checkpoint.created_at),
            "completion_percent": latest_checkpoint.completion_percent
        }
    
    return {"interrupted": False}
```

### Step 2: Validate Checkpoint Data

```python
def validate_checkpoint_for_resume(checkpoint, context_model):
    """
    Check if checkpoint is still valid for resumption.
    Returns: resumable_state (ready | stale | conflicts | restart_needed)
    """
    
    # Check 1: Are upstream artifacts still current?
    upstream_changes = detect_upstream_changes(checkpoint, context_model)
    if upstream_changes:
        if significant_impact(upstream_changes):
            return {
                "resumable": False,
                "reason": "restart_needed",
                "upstream_changed": upstream_changes,
                "impact": "Previous analysis invalid; must restart"
            }
        else:
            return {
                "resumable": True,
                "reason": "resume_with_caution",
                "upstream_changed": upstream_changes,
                "impact": "Some changes; proceed but watch for issues"
            }
    
    # Check 2: Are downstream artifacts conflicted?
    downstream_conflicts = detect_downstream_conflicts(checkpoint, context_model)
    if downstream_conflicts:
        return {
            "resumable": False,
            "reason": "conflicts_need_resolution",
            "conflicts": downstream_conflicts,
            "action": "Resolve conflicts first, then retry"
        }
    
    # Check 3: Is checkpoint data valid?
    checkpoint_valid = validate_checkpoint_integrity(checkpoint)
    if not checkpoint_valid:
        return {
            "resumable": False,
            "reason": "checkpoint_corrupted",
            "action": "Restart from beginning"
        }
    
    # All checks passed
    return {
        "resumable": True,
        "reason": "ready_to_resume",
        "safe_to_continue": True
    }


def detect_upstream_changes(checkpoint, context_model):
    """
    Compare artifact versions at checkpoint time vs. now.
    """
    changes = []
    
    for artifact_id, version_info in checkpoint.upstream_versions.items():
        artifact = context_model.get_artifact(artifact_id)
        current_version = artifact.version
        version_at_read = version_info['version_at_read']
        
        if current_version > version_at_read:
            # Upstream changed
            changelog = context_model.get_changelog(
                artifact_id,
                from_version=version_at_read,
                to_version=current_version
            )
            changes.append({
                "artifact_id": artifact_id,
                "version_at_checkpoint": version_at_read,
                "current_version": current_version,
                "changes": changelog
            })
    
    return changes if changes else []
```

### Step 3: Reconstruct Work State

```python
def reconstruct_work_state(checkpoint, context_model):
    """
    Load checkpoint and prepare to resume.
    Returns: work_state (ready to execute from checkpoint)
    """
    
    # Load checkpoint data
    work_state = {
        "skill_id": checkpoint.skill_id,
        "work_item_id": checkpoint.work_item_id,
        "current_artifact": checkpoint.current_artifact,
        
        # Progress
        "items_processed": checkpoint.items_processed,
        "items_total": checkpoint.items_total,
        "completion_percent": checkpoint.completion_percent,
        
        # Results so far
        "results": {
            "analyzed": checkpoint.intermediate_results.analyzed_requirements,
            "pending": checkpoint.intermediate_results.pending_requirements,
            "issues": checkpoint.intermediate_results.issues_found,
            "decisions_needed": checkpoint.intermediate_results.decisions_needed
        },
        
        # What changed upstream (if any)
        "upstream_changes": detect_upstream_changes(checkpoint, context_model),
        
        # Execution context
        "resume_from": f"analyze_{checkpoint.current_artifact.kind}_{checkpoint.current_artifact.id}",
        "checkpoint_id": checkpoint.id
    }
    
    return work_state
```

### Step 4: Decide: Resume or Restart

```python
def decide_resume_or_restart(checkpoint, validation_result, context_model):
    """
    Given validation result, decide whether to resume or restart.
    """
    
    if not validation_result['resumable']:
        reason = validation_result['reason']
        
        if reason == "restart_needed":
            return {
                "decision": "restart",
                "reason": "Upstream changed significantly",
                "action": "Start from beginning with latest artifacts",
                "parent_checkpoint": checkpoint.id  # For audit trail
            }
        
        elif reason == "conflicts_need_resolution":
            return {
                "decision": "escalate",
                "reason": "Downstream conflicts detected",
                "action": "Create decision_escalation; retry after resolution",
                "parent_checkpoint": checkpoint.id
            }
        
        elif reason == "checkpoint_corrupted":
            return {
                "decision": "restart",
                "reason": "Checkpoint data corrupted",
                "action": "Discard checkpoint; start fresh",
                "parent_checkpoint": checkpoint.id
            }
    
    # Resumable
    else:
        reason = validation_result['reason']
        
        if reason == "ready_to_resume":
            return {
                "decision": "resume",
                "reason": "No conflicts; safe to continue",
                "action": f"Resume from {checkpoint.completion_percent}%",
                "parent_checkpoint": checkpoint.id
            }
        
        elif reason == "resume_with_caution":
            return {
                "decision": "resume_with_monitoring",
                "reason": "Some upstream changes; watch for issues",
                "upstream_changes": validation_result['upstream_changed'],
                "action": f"Resume from {checkpoint.completion_percent}%; monitor for anomalies",
                "parent_checkpoint": checkpoint.id
            }


def create_parent_checkpoint_record(old_checkpoint_id, decision):
    """
    Record the resume decision in context (for audit trail).
    """
    parent_record = {
        "prior_checkpoint": old_checkpoint_id,
        "resume_decision": decision['decision'],
        "reason": decision['reason'],
        "timestamp": timestamp_now(),
        "action_taken": decision['action']
    }
    return parent_record
```

### Step 5: Resume Execution

```python
def resume_from_checkpoint(checkpoint, work_state):
    """
    Re-enter skill at correct point with correct context.
    """
    
    skill_context = {
        "checkpoint_id": checkpoint.id,
        "resume_point": work_state['resume_from'],
        "progress": {
            "processed": work_state['items_processed'],
            "total": work_state['items_total'],
            "percent": work_state['completion_percent']
        },
        "results": work_state['results'],
        "upstream_changes": work_state['upstream_changes']
    }
    
    # Re-enter skill at correct point
    # For requirement analyzer: resume analyzing next requirement
    # For spec writer: resume writing next section
    
    return skill_context
```

---

## 4. Integration with Staleness & Cascades

### How Resumed Skills Handle Changes

```
Checkpoint saved: FR-001, FR-002, FR-003 current
Meanwhile: FR-003 changes (upstream write)
  → Cascade starts: FR-003 stale, SPEC-087 stale, WI-042 stale
On resume: Skill detects FR-003 changed
  → Reads invalidated_by chain: [ADR-003, FR-001, SPEC-002]
  → Decides: "FR-003 affected by ADR change; must re-analyze"
  → Re-processes FR-003 before continuing
```

### Decision: Invalidate Checkpoints on Cascade?

When staleness cascade fires, should existing checkpoints be invalidated?

**Option A: Mark checkpoints stale**
- Pro: Forces re-validation of work
- Con: Throws away work; user loses progress

**Option B: Mark checkpoints with warning**
- Pro: Preserves work; alerts user to changes
- Con: Skill must handle "resume with modifications"

**Recommended: Option B**
- Checkpoint remains resumable but includes upstream change notification
- Skill chooses: proceed with caution, or restart

---

## 5. Resumability Entity (P0-02 Context Schema Addition)

### New Entity Kind: checkpoint

```yaml
checkpoint:
  kind: "checkpoint"
  
  # Identity
  id: string (CP-001)
  created_at: timestamp
  skill_id: string (requirement_analyzer_v2)
  
  # Work Context
  work_item_id: string (WI-042)
  phase: string (requirements | design | implementation | verification)
  stage: string (current execution stage)
  
  # Current Artifact
  current_artifact: {
    id: string
    kind: string
    version: number
    validation_status: string
  }
  
  # Progress
  items_processed: number
  items_total: number
  completion_percent: number
  
  # Results
  intermediate_results: {
    analyzed: [list of artifact ids]
    pending: [list of artifact ids]
    issues_found: [list]
    decisions_needed: [list]
  }
  
  # State Preservation
  upstream_versions: {
    [artifact_id]: {version_at_read, current_version}
  }
  checkpoint_data: blob
  checkpoint_size_bytes: number
  storage_location: string
  
  # Lifecycle
  status: enum (active, superseded, cleaned_up)
  parent_checkpoint: string (if this is a retry)
  resume_decision: string (resume | restart | escalate)
  resume_timestamp: timestamp (when/if resumed)
```

---

## 6. Acceptance Criteria

Resumability implementation is complete when:

- [ ] **AC-1:** Checkpoint model defined (work state, progress, results)
- [ ] **AC-2:** Checkpoint creation on every milestone (not expensive)
- [ ] **AC-3:** Interruption detection (finds active checkpoint)
- [ ] **AC-4:** Checkpoint validation (detect upstream changes)
- [ ] **AC-5:** Work state reconstruction (load checkpoint, prepare to resume)
- [ ] **AC-6:** Resume/restart/escalate decision logic
- [ ] **AC-7:** Resume execution (re-enter skill at correct point)
- [ ] **AC-8:** Staleness integration (detect cascade during resume)
- [ ] **AC-9:** Worked examples (3 interrupt scenarios with recovery)
- [ ] **AC-10:** Checkpoint cleanup (old ones removed after > 7 days)

---

## 7. Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-24 | Checkpoint model + interruption detection | TBD | In progress |
| 2026-08-25 | Checkpoint validation + staleness detection | TBD | Not started |
| 2026-08-26 | Work state reconstruction + resume logic | TBD | Not started |
| 2026-08-27 | Resume/restart/escalate decision tree | TBD | Not started |
| 2026-08-28 | Worked examples + design complete | TBD | Not started |

---

## 8. Open Questions

1. **How long to keep checkpoints?** (Suggested: 7 days, then cleanup)
2. **How often to create checkpoints?** (Suggested: every 5 min or after artifact completes)
3. **Should checkpoints be versioned?** (Yes, per checkpoint_sequence)
4. **Can skills customize checkpoint frequency?** (Yes, per skill config)
5. **What about multi-skill workflows (one starts while another paused)?** (Separate checkpoints per skill)

---

**P0-05 Design: Resumability — READY FOR TEAM EXECUTION**

Next: Assign Design Engineer #2 to complete by 2026-08-28.
