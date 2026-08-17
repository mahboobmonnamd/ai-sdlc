# P0-01: Routing & Precedence

**Workstream:** P0-01  
**Title:** Routing & Precedence Algorithm  
**Status:** Design Phase  
**Design Lead:** TBD  
**Start Date:** 2026-08-17  
**Target Completion:** 2026-08-22 (5 days)  
**Depends On:** P0-02 (Context Data Model) ✅ COMPLETE  

---

## Executive Summary

**Problem:** When a skill encounters multiple possible next steps (e.g., clarify requirement, write spike, raise decision), how does it decide which to pursue? Traditional numeric scoring (60% credibility + 40% priority) appears precise but hides wrong routing logic.

**Solution:** Deterministic **precedence cascade**—a yes/no decision tree that routes based on blocking conditions in priority order:

1. **Is work blocked by unresolved decision?** → Escalate & wait
2. **Does this require decision authority outside the skill?** → Escalate & wait
3. **Is there technical uncertainty?** → Spike first
4. **Are required artifacts missing or stale?** → Create/refresh artifacts
5. **All preconditions met?** → Ready to execute

**Outcome:** Clear, auditable routing. Skills follow the same logic regardless of project or context. No hidden assumptions.

---

## 1. Design Rationale

### Why Precedence Instead of Scoring?

**Scoring Approach (Wrong):**
```
Next step score = (0.60 × credibility) + (0.40 × priority)
If FR-001: credibility=85%, priority=70% → score = 78%
If SPIKE-001: credibility=45%, priority=60% → score = 52%
→ Route to FR-001

Problem: What if credibility=45% is actually "critical uncertainty"?
Numeric score hides that. Skill proceeds with 45% confidence.
```

**Precedence Approach (Correct):**
```
Is there unresolved uncertainty? → YES → Do spike first (blocks everything)
Is required decision missing? → YES → Escalate (blocks everything)
All preconditions met? → YES → Proceed with FR-001

No false precision. Uncertainty is explicit.
```

### Why This Matters for AI Skills

Skills operate autonomously. Wrong routing decisions compound:
- **Mistake 1:** Skill ignores spike, implements FR with wrong assumption
- **Mistake 2:** Verification fails, artifact marked stale
- **Mistake 3:** Multi-agent conflict: did skill miss a blocker? or did context change?

Precedence cascade makes routing auditable: "At time T, we had blocker B1, decision D2 unresolved, uncertainty U1. Skill was directed to spike first. That was correct."

### Design Constraints

1. **Deterministic:** Same inputs → same routing (no randomness or tie-breaking)
2. **Auditable:** Can explain why next step was chosen
3. **Skill-agnostic:** Routing logic independent of skill domain
4. **Stageable:** Some gates can be skipped if context says "already verified"
5. **Resumable:** If session interrupted, same routing decision is reconstructed

---

## 2. Precedence Cascade (Decision Tree)

### Full Cascade

```
START: Evaluate next step for [artifact]
│
├─ Gate 1: BLOCKING DECISION
│  │
│  ├─ Is there a decision_escalation entity with
│  │  │  status = "unresolved" AND
│  │  │  affects this artifact?
│  │  │
│  │  ├─ YES → ROUTE: Escalate & Wait
│  │  │         (decision must be made before progress)
│  │  │
│  │  └─ NO → Continue to Gate 2
│  │
│  └─ [DECISION_ESCALATION entity links decisions to work items]
│
│
├─ Gate 2: AUTHORITY REQUIRED
│  │
│  ├─ Does this step require decision authority
│  │  │  outside current skill's scope?
│  │  │  (e.g., requirement change, rigor profile change, architecture)
│  │  │
│  │  ├─ YES → ROUTE: Escalate (human/authority decides)
│  │  │         [E.g., "Update FR-001" requires product authority]
│  │  │
│  │  └─ NO → Continue to Gate 3
│  │
│  └─ [AUTHORITY mapping in context model]
│
│
├─ Gate 3: TECHNICAL UNCERTAINTY
│  │
│  ├─ Is there unresolved uncertainty blocking this?
│  │  │  (spike_finding not yet available, API contract undefined, etc.)
│  │  │
│  │  ├─ YES → ROUTE: Spike (explore & resolve uncertainty)
│  │  │         [E.g., "Design database schema first"]
│  │  │
│  │  └─ NO → Continue to Gate 4
│  │
│  └─ [SPIKE entities with status=active in depends_on]
│
│
├─ Gate 4: ARTIFACT QUALITY
│  │
│  ├─ Are required artifacts (spec, requirement, decision)
│  │  │  present and valid (validation_status = current)?
│  │  │
│  │  ├─ NO → ROUTE: Create or Refresh Artifact
│  │  │        [E.g., "Write specification before implementation"]
│  │  │        [E.g., "Requirement marked stale; re-validate"]
│  │  │
│  │  └─ YES → Continue to Gate 5
│  │
│  └─ [VALIDATION_STATUS from P0-02 context model]
│
│
├─ Gate 5: PREREQUISITE WORK
│  │
│  ├─ Are upstream work items complete?
│  │  │  (depends_on: [WI-001, WI-002])
│  │  │
│  │  ├─ NO → ROUTE: Block (wait for upstream)
│  │  │        [E.g., "Cannot test until WI-001 implemented"]
│  │  │
│  │  └─ YES → Continue to Gate 6
│  │
│  └─ [WORK_ITEM status = "complete" or "verified"]
│
│
├─ Gate 6: BLOCKED BY RISK
│  │
│  ├─ Is this blocked by an unmitigated risk?
│  │  │  (risk with status = "active" and blocks this artifact)
│  │  │
│  │  ├─ YES → ROUTE: Mitigate Risk First
│  │  │        [E.g., "Resolve security risk before deployment"]
│  │  │
│  │  └─ NO → Continue to Gate 7
│  │
│  └─ [RISK entities with blocks relationships]
│
│
└─ Gate 7: READY TO EXECUTE
   │
   ├─ YES → ROUTE: Proceed with current artifact
   │        (all preconditions met)
   │
   └─ End
```

### Gate Priority (Why This Order?)

| Priority | Gate | Reason |
|----------|------|--------|
| 1 | Blocking Decision | Decisions override everything; can't proceed without them |
| 2 | Authority Required | Some changes need approval; can't bypass authority |
| 3 | Technical Uncertainty | Spikes must happen before implementation (highest risk if skipped) |
| 4 | Artifact Quality | Stale/missing artifacts cause rework (medium risk) |
| 5 | Prerequisite Work | Upstream must complete (scheduling risk) |
| 6 | Unmitigated Risk | Risk mitigation blocks deployment (safety risk) |
| 7 | Ready | Default: proceed |

---

## 3. Routing State Machine

### State Definitions

```
State: "awaiting_decision"
├─ Trigger: Gate 1 fires (unresolved decision_escalation found)
├─ Action: Stop forward progress; record blocking decision
├─ Resume Condition: decision_escalation.status = "resolved"
├─ Timeout: None (wait indefinitely until decision made)
└─ Context: decision_escalation entity with decision options logged

State: "awaiting_authority"
├─ Trigger: Gate 2 fires (authority required)
├─ Action: Escalate to authority; present options + tradeoffs
├─ Resume Condition: Authority responds with approval
├─ Timeout: Optional (per project config: e.g., 24h escalation timeout)
└─ Context: What decision? Who has authority? (from P0-08 escalation model)

State: "spiking"
├─ Trigger: Gate 3 fires (technical uncertainty)
├─ Action: Create spike work_item; research + document findings
├─ Resume Condition: spike_finding documented; artifact marked valid
├─ Timeout: Per spike.max_duration (e.g., 3 days)
└─ Context: What's uncertain? What spike resolves it?

State: "artifact_missing"
├─ Trigger: Gate 4 fires (artifact not present)
├─ Action: Create artifact (spec, requirement, decision)
├─ Resume Condition: New artifact created + validated
├─ Timeout: None (artifact must exist)
└─ Context: Which artifact? Artifact template from rigor profile

State: "artifact_stale"
├─ Trigger: Gate 4 fires (validation_status = stale|needs_recheck)
├─ Action: Revalidate artifact; update if changed
├─ Resume Condition: Re-run validation; status = current
├─ Timeout: Per artifact type (e.g., 7 days for spec, 1d for requirement)
└─ Context: What changed? Why is it stale? (from invalidated_by chain)

State: "blocked_upstream"
├─ Trigger: Gate 5 fires (prerequisite work_item not complete)
├─ Action: Wait for upstream; optionally offer to unblock upstream
├─ Resume Condition: Upstream work_item.status = complete|verified
├─ Timeout: Per project (e.g., 48h escalation if upstream blocked too)
└─ Context: Which upstream work? Is it also blocked?

State: "risk_unmitigated"
├─ Trigger: Gate 6 fires (active risk blocks this artifact)
├─ Action: Execute risk mitigation plan
├─ Resume Condition: risk.status = mitigated
├─ Timeout: Per risk.mitigation_deadline
└─ Context: What's the risk? Mitigation plan?

State: "ready"
├─ Trigger: Gate 7 passes (all preconditions met)
├─ Action: Proceed with next step (implement, verify, etc.)
├─ Resume Condition: N/A (execute immediately)
├─ Timeout: N/A
└─ Context: Skill now has full autonomy for this artifact
```

### State Transitions (Decision Table)

| Current State | Trigger | → New State | Action | Resume When |
|---|---|---|---|---|
| START | Blocker decision unresolved | awaiting_decision | Escalate | Decision made |
| START | Authority needed | awaiting_authority | Escalate | Authority approves |
| START | Technical uncertainty | spiking | Create spike | Spike complete |
| START | Artifact missing | artifact_missing | Create artifact | Artifact exists |
| START | Artifact stale | artifact_stale | Revalidate | Valid status |
| START | Upstream incomplete | blocked_upstream | Wait | Upstream complete |
| START | Risk unmitigated | risk_unmitigated | Mitigate | Risk resolved |
| START | All gates pass | ready | Execute | N/A |
| awaiting_decision | Decision made | START | Restart evaluation | (recursive) |
| awaiting_authority | Authority approves | START | Restart evaluation | (recursive) |
| spiking | Spike complete | START | Restart evaluation | (recursive) |
| artifact_missing | Artifact created | START | Restart evaluation | (recursive) |
| artifact_stale | Validation complete | START | Restart evaluation | (recursive) |
| blocked_upstream | Upstream complete | START | Restart evaluation | (recursive) |
| risk_unmitigated | Risk resolved | START | Restart evaluation | (recursive) |
| ready | Action complete | (next artifact) | Evaluate next step | (recursive) |

**Note:** "Restart evaluation" means run full cascade again. Context may have changed.

---

## 4. Routing Examples

### Example 1: Greenfield Idea → Implementation

**Context:** User requests "Build user auth feature"

```
Step 1: Evaluate "Implement user auth"
├─ Gate 1 (Blocking decision): Are there unresolved decisions?
│  └─ decision_escalation: "What auth scheme? OAuth? JWT? Session?" (unresolved)
│  └─ ROUTE: Escalate & Wait
│
[Authority resolves: "Use JWT"]
│
Step 2: Evaluate again
├─ Gate 1 (Blocking decision): Resolved ✓
├─ Gate 2 (Authority): Do we need authority to implement JWT?
│  └─ NO (technical decision, skill has authority)
│  └─ Continue
├─ Gate 3 (Uncertainty): Is JWT implementation well-defined?
│  └─ YES (standard library exists, we have examples)
│  └─ Continue
├─ Gate 4 (Artifacts): Do we have requirement + spec?
│  └─ requirement.yaml exists, FR-042 = "JWT auth required"
│  └─ spec.yaml exists, SPEC-087 = "JWT + refresh token"
│  └─ Both marked validation_status = "current"
│  └─ Continue
├─ Gate 5 (Upstream): Are dependencies complete?
│  └─ WI-001 (Database schema) = "verified"
│  └─ Continue
├─ Gate 6 (Risk): Unmitigated risks?
│  └─ risk.yaml: RISK-003 = "Token expiry edge case" (status=mitigated)
│  └─ Continue
│
└─ Gate 7 (Ready): YES → ROUTE: Proceed with Implementation
   └─ Skill now implements WI-042 (JWT auth)
```

### Example 2: Mid-Implementation Artifact Change (Staleness Cascade)

**Context:** Developer discovers requirement incomplete during implementation.

```
Step 1: Skill implementing WI-042 (JWT auth)
├─ Encounters: "How long should tokens live?"
├─ Realizes: FR-042 doesn't specify TTL
│
Step 2: Skill marks FR-042 as stale
├─ FR-042.invalidated_by = "discovered_gap_during_implementation"
├─ FR-042.validation_status = "needs_recheck"
├─ P0-03 cascade logic marks affected entities stale:
│  ├─ SPEC-087 depends_on FR-042 → SPEC-087.validation_status = stale
│  ├─ WI-042 depends_on SPEC-087 → WI-042.validation_status = stale
│  └─ VER-199 depends_on WI-042 → VER-199.validation_status = stale
│
Step 3: Next routing evaluation for WI-042
├─ Gate 1 (Blocking decision): Is there new decision_escalation?
│  └─ YES: "How long should JWT tokens live?" (escalation created)
│  └─ ROUTE: Escalate & Wait
│
[Authority resolves: "TTL = 1 hour"]
[Requirement updated: FR-042 += TTL]
[FR-042.validation_status = current]
│
Step 4: Cascade revalidation (P0-03 logic)
├─ SPEC-087 validation_status = stale (but depends_on FR-042, now current)
│  └─ Revalidate SPEC-087 against updated FR-042
│  └─ SPEC-087 += "TTL=1h" detail
│  └─ SPEC-087.validation_status = current
├─ WI-042 revalidated
│  └─ WI-042 += "Test token expiry after 1h"
│  └─ WI-042.validation_status = current
│
Step 5: Re-route WI-042
├─ Gate 1 (Blocking decision): Resolved ✓
├─ Gate 2 (Authority): Resolved ✓
├─ Gate 3 (Uncertainty): "How to test 1h timeout?" (new uncertainty)
│  └─ ROUTE: Spike (how to test time-dependent behavior)
│
[Spike created: SPIKE-003 "Test time-dependent JWT expiry"]
[Spike finds: Use time mock library, documented in spike_finding]
│
Step 6: Re-route WI-042 again
├─ All gates pass
└─ ROUTE: Proceed with Implementation (now with TTL + test strategy)
```

### Example 3: Multi-Skill Conflict Scenario

**Context:** Two skills working on same artifact; one discovers blocker.

```
Skill A (Implementing): Working on WI-050 (database migration)
Skill B (Verifying): Validating WI-050
│
Time T1: Skill B discovers issue
├─ Verification fails: "Migration doesn't handle null_timestamp"
├─ Skill B marks WI-050 as needing rework
├─ Skill B creates decision_escalation: "Can we skip null timestamps? (breaking change)"
│
Time T2: Skill A (next routing cycle) evaluates WI-050
├─ Gate 1 (Blocking decision):
│  └─ decision_escalation: "null_timestamp strategy" (unresolved)
│  └─ ROUTE: Escalate & Wait
├─ Skill A stops; does NOT continue with implementation
├─ Skill A records: "Blocked by verification issue at WI-050"
│
Time T3: Authority resolves
├─ Authority updates FR-045: "Null timestamps → set to current_time"
├─ decision_escalation marked "resolved"
│
Time T4: Skill A re-evaluates WI-050
├─ Gate 1: Resolved ✓
├─ Gate 3: "Does migration handle null check correctly?" (spike needed)
│  └─ ROUTE: Spike
│
[Spike: Implement null check; verify with test cases]
│
Time T5: Skill A re-evaluates WI-050
├─ All gates pass
└─ ROUTE: Proceed with implementation (now with null handling)
│
Time T6: Skill B re-validates WI-050
└─ Verification passes ✓
```

### Example 4: Rigor Profile Affects Artifact Quality Gate

**Context:** Same project, different work streams at different rigor levels.

```
Project Config: Rigor Profile = "Standard"

Workstream A: Core auth (Standard rigor)
├─ WI-042 (JWT auth) requires:
│  ├─ requirement.yaml (required)
│  ├─ specification.yaml (required)
│  └─ verification.yaml (required)
│
Workstream B: Admin UI (Lightweight rigor)
├─ WI-051 (Admin dashboard) requires:
│  ├─ requirement.yaml (required)
│  └─ acceptance_criteria (required)
│  └─ specification.yaml (OPTIONAL)
│
Step 1: Skill evaluates WI-042 (JWT, Standard)
├─ Gate 4 (Artifacts): Check required artifacts
│  ├─ requirement? YES ✓
│  ├─ specification? YES ✓
│  ├─ verification template? YES ✓
│  └─ All present and current → Continue
│
Step 2: Skill evaluates WI-051 (Admin UI, Lightweight)
├─ Gate 4 (Artifacts): Check required artifacts (per Lightweight profile)
│  ├─ requirement? YES ✓
│  ├─ acceptance_criteria? YES ✓
│  ├─ specification? SKIPPED (optional in Lightweight)
│  └─ All required present → Continue
│
Note: Same Gate 4, but different artifact requirements per rigor profile.
(Rigor profile stored in context; routing logic checks it.)
```

---

## 5. Ambiguity Resolution

### When Precedence Cascade Doesn't Decide Uniquely

**Scenario:** All gates pass; multiple next steps equally valid:
- Option A: Implement feature now
- Option B: Write more tests first
- Option C: Refactor existing code for consistency

**Decision:** Use **ranking** as tiebreaker, not primary routing:

```
Condition: Gate 7 passes (all preconditions met)
         AND multiple next steps equally valid

Tiebreaker Ranking:
  1. Does user specify preference? (e.g., "tests first")
     └─ YES → Follow user preference
  2. Is there a priority signal in context? (e.g., release deadline)
     └─ YES → Route to highest priority work
  3. Is there risk mitigation priority? (e.g., high-risk code)
     └─ YES → Route to verification first
  4. Default: Lexicographic order (alphabetical by artifact_id)
     └─ Deterministic tie-break; no randomness

Result: Still deterministic. Audit trail shows why choice was made.
```

**Constraints on Ambiguity:**
- Ambiguity only appears AFTER all precedence gates pass
- If gates create blockage, no ambiguity (forced routing)
- Ambiguity resolution is optional per project (can disable tie-breaking)

---

## 6. Integration with P0-02 Context Model

### Context Entities Used in Routing

| Entity Type | Routing Gate | Field Checked |
|---|---|---|
| `decision_escalation` | Gate 1 | status = unresolved? |
| `requirement`, `specification`, `verification` | Gate 4 | validation_status = current? |
| `spike` | Gate 3 | status = active? Has spike_finding? |
| `work_item` | Gate 5 | status = complete or verified? |
| `risk` | Gate 6 | status = active? Blocks this artifact? |
| `decision` | Gate 2 | authority field matches skill scope? |

### Routing Writes to Context

When routing changes state, it updates context:

```yaml
decision_escalation:
  - id: ESCA-42
    status: unresolved → resolved (after authority responds)
    resolved_by: Authority ID
    resolved_at: timestamp
    resolution: "Use JWT, 1h TTL"
    
work_item:
  - id: WI-042
    validation_status: current → stale (when upstream changes)
    invalidated_by: FR-042 change
    last_revalidation: timestamp
    
spike:
  - id: SPIKE-003
    status: active → complete
    spike_finding: "[detailed findings]"
    resolved_at: timestamp
```

All routing decisions are auditable via context.

---

## 7. Acceptance Criteria

Routing implementation is complete when:

- [ ] **AC-1:** Precedence cascade decision tree can evaluate any (artifact, context) pair and produce routing decision
- [ ] **AC-2:** Routing decision is deterministic (same inputs → same output)
- [ ] **AC-3:** Routing decision is auditable (can explain why, what gates fired, what context values mattered)
- [ ] **AC-4:** State machine handles all 7 states + transitions without deadlock
- [ ] **AC-5:** All 6 routing examples (above) can be traced through cascade and produce correct states
- [ ] **AC-6:** Ambiguity tiebreaker produces deterministic choice when multiple next steps valid
- [ ] **AC-7:** Rigor profile changes routing (Lightweight vs. Standard vs. High-rigor require different artifacts)
- [ ] **AC-8:** Context schema (P0-02) is sufficient to express all routing gates (decision_escalation, validation_status, dependencies, etc.)
- [ ] **AC-9:** Integration with P0-08 (Decision Escalation) behavior: routing produces decision_escalation state that escalation workflow can consume
- [ ] **AC-10:** Worked examples are reproducible and match live system behavior (P0-09 validation will test this)

---

## 8. Decision Log

### Decision: Precedence Cascade Instead of Scoring

**Decision:** Routing uses deterministic precedence cascade (yes/no gates), not numeric scoring.

**Alternatives Considered:**
1. Numeric scoring (e.g., 60% credibility + 40% priority)
2. Machine learning (train on past routing decisions)
3. Greedy best-fit (always pick "best" next step)
4. Random among top N (if tied, pick randomly)

**Why This Decision:**
- Transparent: Anyone can trace why a step was chosen
- Auditable: Can reconstruct routing decision from context
- Safe: Blocks before proceeding (vs. scoring which hides uncertainty)
- Skill-agnostic: Same logic for all domains
- Resumable: Session interruption doesn't affect routing consistency

**Trade-offs:**
- Pro: Clear reasoning
- Con: May seem rigid (but ambiguity resolution allows flexibility)

**Status:** LOCKED  
**Date:** 2026-08-17  
**Rationale:** User's correction: scoring hides wrong routing; precedence makes it explicit

---

### Decision: Gate Priority Order (Blocking → Authority → Uncertainty → Artifacts → Upstream → Risk → Ready)

**Decision:** Precedence gates ordered as: blocking decision, authority, uncertainty, artifacts, upstream work, risk, ready.

**Rationale:**
- Decisions are highest priority (can't proceed without them)
- Authority is next (some changes require approval)
- Uncertainty is next (must spike before implementing with wrong assumptions)
- Artifacts are next (need spec/requirement to implement against)
- Upstream work is next (scheduling constraint)
- Risk is last (safety constraint before release)

**Status:** LOCKED  
**Date:** 2026-08-17

---

### Decision: Ambiguity Tiebreaker via Ranking (Not Scoring)

**Decision:** When multiple next steps equally valid (all gates pass), use ranking (user preference → priority signal → risk signal → lexicographic).

**Rationale:**
- Maintains determinism (no randomness)
- Still transparent (why was this chosen?)
- Allows optionality (user can override)

**Status:** LOCKED  
**Date:** 2026-08-17

---

### Decision: Rigor Profile Affects Gate 4 (Artifact Requirements)

**Decision:** Gate 4 (Artifact Quality) checks different artifacts depending on rigor profile.

**Rationale:**
- Lightweight projects don't need full specs; Standard and High do
- Same routing logic; different inputs per profile
- Allows flexible rigor without routing logic fragmentation

**Depends On:** P0-06 (Rigor Profiles design)  
**Status:** PENDING  
**Date:** TBD

---

## 9. Open Questions for Phase 0 Team

1. **Should Gate 4 also check relationships?** E.g., "Does requirement reference non-existent specification?"
2. **Should routing loop (Gate 1 fired → resolve → Gate 1 again) be automatic or manual trigger?**
3. **Should precedence cascade be configurable per project?** Or always fixed?
4. **How long should we wait in "awaiting_decision" state before timeout escalation?** (Project config? Default?)
5. **Should ambiguity tiebreaker be project-configurable (user vs. priority vs. lexicographic) or always same order?**

---

## 10. Next Documents

After P0-01 complete, proceed with:
- **P0-03:** Staleness & Invalidation (how cascade works when context changes)
- **P0-04:** Multi-Agent Consistency (how routing handles concurrent skill updates)

---

## Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-17 | Design precedence cascade | TBD | In progress |
| 2026-08-18 | Create decision table + state machine | TBD | Not started |
| 2026-08-19 | Write 4+ worked examples | TBD | Not started |
| 2026-08-20 | Integration review (P0-02, P0-08 teams) | TBD | Not started |
| 2026-08-22 | Design complete + ready for P0-09 | TBD | Not started |

---

**P0-01 Design: Routing & Precedence — READY FOR TEAM EXECUTION**

Next: Assign Design Engineer #1 to complete by 2026-08-22.
