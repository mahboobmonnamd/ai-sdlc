# P0-08: Decision Escalation

**Workstream:** P0-08  
**Title:** Decision Escalation Workflow & Authority Resolution  
**Status:** Design Phase  
**Design Lead:** TBD (Design Engineer #2)  
**Start Date:** 2026-08-24  
**Target Completion:** 2026-08-28 (4 days)  
**Depends On:** P0-01 (Routing: awaiting_decision state) ✅  

---

## Executive Summary

**Problem:** When routing detects an unresolved decision, what happens?
- How do we escalate to the right authority?
- How do we present options and trade-offs?
- How do we resume after decision is made?
- How do we prevent deadlock (waiting forever for undecidable question)?

**Solution:** Define 8-step escalation workflow that:
1. Stops skill execution
2. Explains the blocking decision
3. Presents options with trade-offs
4. Routes to correct authority
5. Records unresolved state for audit
6. Resumes skill execution when decision arrives
7. Handles timeouts and escalation appeals

**Outcome:** Decisions are made explicitly, traced, and documented. No silent assumptions.

---

## 1. Design Rationale

### Why Explicit Escalation Matters

**Without escalation:**
```
Skill encounters: "Should auth be OAuth or JWT?"
Skill assumes: "Both are fine; I'll pick JWT"
Later: "Why did we choose JWT?"
Answer: "Unknown; someone picked it"
Result: Wrong choice for actual requirements
```

**With escalation:**
```
Skill encounters: "Should auth be OAuth or JWT?"
Step 1: Create decision_escalation with decision_topic
Step 2: Document trade-offs (OAuth: social login, JWT: custom control)
Step 3: Route to authority (product/tech lead)
Step 4: Authority decides: "Use OAuth for MVP"
Step 5: Escalation marked resolved with decision
Step 6: Skill resumes with decided direction
Step 7: Audit trail shows who decided, when, why
```

### Design Constraints

1. **Deterministic:** Same decision scenario → same escalation flow
2. **Non-Blocking:** Skill execution stops, doesn't hang or timeout silently
3. **Auditable:** Full record of decision, options, authority, resolution
4. **Resumable:** After decision, skill execution resumes correctly
5. **Timeout-Protected:** If authority unresponsive, escalation escalates further
6. **Authority-Aware:** Routes to correct authority type (product, tech, security, etc.)

---

## 2. Eight-Step Escalation Workflow

### Step 1: Skill Detects Unresolved Decision

```python
def routing_gate_1_blocking_decision(artifact, context_model):
    """
    Gate 1: Check if unresolved decision blocks this artifact.
    If yes, trigger escalation workflow.
    """
    unresolved_escalations = context_model.filter_by_relationship(
        kind="decision_escalation",
        affects=artifact.id,
        status="unresolved"
    )
    
    if unresolved_escalations:
        escalation = unresolved_escalations[0]
        trigger_escalation_workflow(escalation, artifact, context_model)
        return {
            "routing_decision": "awaiting_decision",
            "escalation_id": escalation.id
        }
```

### Step 2: Create Decision_Escalation Entity

```yaml
decision_escalation:
  id: ESCA-001
  kind: decision_escalation
  status: unresolved
  created_at: 2026-08-24T14:30:00Z
  created_by: routing_skill
  
  # Decision details
  decision_topic: "What authentication scheme? OAuth, JWT, or Session tokens?"
  decision_description: "User authentication for web app"
  blocking_work_item: WI-042
  
  # Context
  context: 
    problem: "FR-001 requires user auth but doesn't specify how"
    constraints: 
      - "Must support social login"
      - "Must scale to 1M users"
      - "Must be industry-standard"
    dependencies: [FR-001, ADR-002]
  
  # Options
  options:
    - id: OPT-A
      name: "OAuth 2.0"
      description: "Use industry-standard OAuth"
      pros: [social login, industry standard, reduced burden]
      cons: [third-party dependency, data leakage risk]
      estimated_effort: "3 days"
      estimated_cost: "$500 (service subscription)"
    
    - id: OPT-B
      name: "JWT (custom)"
      description: "Implement JWT in-house"
      pros: [full control, no third-party, zero cost]
      cons: [requires expertise, security risk if wrong, more work]
      estimated_effort: "5 days"
      estimated_cost: "$0"
    
    - id: OPT-C
      name: "Session tokens"
      description: "Traditional server-side sessions"
      pros: [simple, well-understood, good security]
      cons: [doesn't scale to 1M users, not modern]
      estimated_effort: "1 day"
      estimated_cost: "$0"
  
  # Authority
  authority_required: product_lead
  authority_type: product_lead
  authority_deadline: 2026-08-25T17:00:00Z  # Next business day
  
  # Resolution
  resolution: null  # Unresolved
  resolved_by: null
  resolved_at: null
```

### Step 3: Explain the Decision to Authority

**Message to Authority:**

```
Subject: Decision Required: User Authentication Strategy (WI-042)

BLOCKING: This decision is blocking work item WI-042 "Implement user auth"

DECISION: Which authentication scheme for web app?

CONTEXT:
- User story: Users can log in securely
- Constraints: Social login support, scale to 1M users, industry-standard
- Related: FR-001, ADR-002

OPTIONS:
1. OAuth 2.0
   Pros: Social login, industry standard, reduced burden
   Cons: Third-party dependency, potential data issues
   Effort: 3 days | Cost: $500/month service

2. JWT (custom implementation)
   Pros: Full control, no third-party, zero cost
   Cons: Requires security expertise, more development work
   Effort: 5 days | Cost: $0

3. Session tokens (server-side)
   Pros: Simple, well-understood, secure
   Cons: Doesn't scale to 1M users, not modern architecture
   Effort: 1 day | Cost: $0

DEADLINE: Aug 25, 5 PM

IMPACT OF DELAY:
- WI-042 blocked (implementation waiting)
- SPEC-087 waiting to be finalized (depends on auth decision)
- VER-087 waiting to write test strategy

Please respond with your decision and rationale.
```

### Step 4: Present Options with Trade-offs

**Authority Reviews & Decides**

```yaml
Authority Response:
  authority: product_lead_alice
  response_time: 2026-08-24T16:45:00Z  # Same day!
  decision: OPT-A  # OAuth
  rationale: "Social login is critical for user acquisition. OAuth 2.0 is industry standard, reduces risk."
  risk_acknowledged: "Third-party dependency acceptable; use reputable provider (Auth0)"
  contingency: "If Auth0 becomes unreliable, can migrate to OPT-B (JWT) in 3 days"
  approval_level: product_lead
```

### Step 5: Record Escalation Resolution

```yaml
decision_escalation:
  id: ESCA-001
  status: resolved
  
  # Resolution details
  resolution: "Use OAuth 2.0 (Auth0 provider)"
  resolved_by: product_lead_alice
  resolved_at: 2026-08-24T16:45:00Z
  decision_rationale: "Social login critical; OAuth 2.0 industry standard"
  risk_mitigations: ["Use reputable provider (Auth0)", "Contingency: switch to JWT in 3 days"]
  approval_level: product_lead
  
  # Audit trail
  escalation_duration_minutes: 135  # 2 hours 15 minutes
  appeal_possible_until: 2026-08-26T16:45:00Z  # 48 hours
  appeal_to_authority: cto  # If product_lead's decision questioned
```

### Step 6: Resume Skill Execution

**Routing Re-Evaluates WI-042:**

```python
def resume_after_escalation_resolution(escalation_id, context_model):
    """
    After decision_escalation resolved, re-run routing for affected work item.
    """
    escalation = context_model.get_artifact(escalation_id)
    blocking_artifact_id = escalation.blocking_work_item
    
    # Re-evaluate routing for WI-042
    decision = evaluate_routing_decision(blocking_artifact_id, context_model)
    
    # Now Gate 1 should pass (decision resolved)
    # Routing proceeds to Gate 2, 3, 4, etc.
    
    return decision
```

### Step 7: Update Downstream Artifacts

**Once Decision is Made:**

```yaml
WI-042: "Implement user auth"
  status: not_started → ready_to_implement
  decision_applied: ESCA-001 (OAuth 2.0)

SPEC-087: "JWT authentication spec"
  status: artifact_stale → artifact_missing
  reason: "Spec was JWT-specific; now need OAuth spec"
  action: Create new SPEC-088 (OAuth 2.0 spec)

ADR-004: (new decision record)
  decision: "Use OAuth 2.0 authentication"
  decided_by: product_lead_alice
  date: 2026-08-24
  references: [ESCA-001, WI-042]
```

### Step 8: Handle Timeout & Escalation Appeal

**Timeout Handling:**

```python
def check_escalation_timeout(escalation_id, context_model):
    """
    If authority doesn't respond by deadline, escalate further.
    """
    escalation = context_model.get_artifact(escalation_id)
    
    if escalation.status == "unresolved":
        now = timestamp_now()
        deadline = escalation.authority_deadline
        
        if now > deadline:
            # Timeout reached
            escalation.status = "timeout"
            escalation.escalated_to = escalation.authority_type_higher  # CEO, CTO, etc.
            
            # Send notification to higher authority
            notify_authority(
                message=f"Decision {escalation.id} timed out. Escalating to you.",
                urgency="high"
            )
            
            # New deadline: same day
            escalation.authority_deadline = tomorrow_eod()
            
            return {
                "action": "escalated_further",
                "from_authority": escalation.authority_required,
                "to_authority": escalation.authority_type_higher,
                "reason": "timeout"
            }
```

**Appeal Handling:**

```python
def allow_appeal(escalation_id, context_model):
    """
    Authority can appeal decision within appeal window.
    Routes to higher authority for override.
    """
    escalation = context_model.get_artifact(escalation_id)
    
    if escalation.status == "resolved":
        now = timestamp_now()
        appeal_deadline = escalation.appeal_possible_until
        
        if now < appeal_deadline:
            # Appeal window still open
            # Create new escalation for higher authority
            appeal_escalation = create_decision_escalation(
                parent_escalation=escalation_id,
                type="appeal",
                decision_topic=f"Override decision on {escalation.decision_topic}?",
                authority_required=escalation.appeal_to_authority,
                context="Original decision questioned"
            )
            return appeal_escalation
```

---

## 3. Authority Matrix

### Who Has Authority for What Decision?

```yaml
Authority Levels:

Level 1 - Tech Skill (self-contained)
  Decision: Implementation details (variable naming, function refactoring)
  Authority: Skill itself (no escalation)
  Timeline: Immediate

Level 2 - Team Lead (technical)
  Decisions: Architectural choices (database, framework, auth scheme)
  Examples: "SQL vs NoSQL?", "React vs Vue?", "OAuth vs JWT?"
  Authority: Tech lead / Engineering manager
  Timeline: < 24 hours
  Escalation_to: CTO if team lead unavailable

Level 3 - Product Lead (business)
  Decisions: Feature scope, acceptance criteria, priority
  Examples: "Support iOS?", "Premium tier feature or free?", "1M users or 10M users?"
  Authority: Product lead / Product manager
  Timeline: < 24 hours
  Escalation_to: Head of Product if unavailable

Level 4 - Security Lead (safety)
  Decisions: Security/compliance/privacy choices
  Examples: "Encrypt at rest?", "GDPR compliance?", "Third-party data sharing?"
  Authority: Security lead / CISO
  Timeline: < 48 hours
  Escalation_to: CEO if security risk is critical

Level 5 - CEO (business strategy)
  Decisions: Major business/strategic choices
  Examples: "Partner with competitor?", "Sunset product?", "Change business model?"
  Authority: CEO
  Timeline: < 1 week
  Escalation_to: Board if critical

Authority Routing:
  Technical decision → Tech Lead → CTO → CEO
  Product decision → Product Lead → Head of Product → CEO
  Security decision → Security Lead → CISO → CEO
  Business decision → CEO
```

---

## 4. Decision Escalation Entity (P0-02 Context Schema Addition)

### New Entity Kind: decision_escalation

```yaml
decision_escalation:
  kind: "decision_escalation"
  
  # Identity
  id: string (ESCA-001)
  created_at: timestamp
  created_by: string (skill_id or user_id)
  
  # Decision Details
  decision_topic: string (the question)
  decision_description: string (full context)
  blocking_work_item: string (WI-042)
  
  # Options
  options: array
    - id: string
      name: string
      description: string
      pros: [list]
      cons: [list]
      effort_estimate: string
      cost_estimate: string
  
  # Authority
  authority_required: enum (product_lead, tech_lead, security_lead, cto, ceo)
  authority_deadline: timestamp
  
  # Status
  status: enum (unresolved, in_review, resolved, timeout, appealed, override)
  resolution: string (the decided option)
  resolved_by: string (authority_id)
  resolved_at: timestamp
  decision_rationale: string (why that option?)
  risk_mitigations: [list]
  
  # Audit
  escalation_duration_minutes: number
  appeal_possible_until: timestamp
  appeal_to_authority: enum
  
  # Relationships
  affects: [list of entity_ids] (WI-042, SPEC-087)
  depends_on: [] (no upstream dependencies for escalations)
  source: {file, line, commit} (where was decision needed?)
```

---

## 5. Acceptance Criteria

Decision Escalation implementation is complete when:

- [ ] **AC-1:** 8-step escalation workflow defined (detect → create → explain → present → record → resume → update → handle)
- [ ] **AC-2:** Authority matrix defined (who decides what, escalation chain)
- [ ] **AC-3:** Decision_escalation entity schema defined
- [ ] **AC-4:** Integration with P0-01 routing Gate 1 (awaiting_decision state)
- [ ] **AC-5:** Decision explanation template (what to send to authority)
- [ ] **AC-6:** Timeout mechanism (escalate further if authority unresponsive)
- [ ] **AC-7:** Appeal mechanism (allow override of decisions within window)
- [ ] **AC-8:** Resume logic (re-evaluate routing after decision resolved)
- [ ] **AC-9:** Worked examples (2-3 escalation scenarios traced end-to-end)
- [ ] **AC-10:** Audit trail complete (decision, options, authority, resolution all recorded)

---

## 6. Decision Log

### Decision: Explicit Authority Assignment (vs. Voting)

**Decision:** Single authority per decision (not democratic voting).

**Rationale:** Clear responsibility. Someone owns the decision. Appeals allowed for reconsideration.

**Status:** LOCKED  
**Date:** 2026-08-24

---

### Decision: Timeout Escalates Further (Not Blocking Forever)

**Decision:** If authority doesn't respond by deadline, escalate to higher authority.

**Rationale:** Prevents deadlock. "Nobody decides" is worse than "we made a decision."

**Status:** LOCKED  
**Date:** 2026-08-24

---

## 7. Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-24 | 8-step workflow + authority matrix | TBD | In progress |
| 2026-08-25 | Decision escalation entity schema | TBD | Not started |
| 2026-08-26 | Timeout + appeal logic | TBD | Not started |
| 2026-08-27 | Integration with routing Gate 1 | TBD | Not started |
| 2026-08-28 | Worked examples + design complete | TBD | Not started |

---

**P0-08 Design: Decision Escalation — READY FOR TEAM EXECUTION**

Next: Assign Design Engineer #2 to complete by 2026-08-28.
