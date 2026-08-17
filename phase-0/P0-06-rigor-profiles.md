# P0-06: Rigor Profiles

**Workstream:** P0-06  
**Title:** Rigor Profiles: Lightweight, Standard, High-Rigor  
**Status:** Design Phase  
**Design Lead:** TBD (Design Engineer #2)  
**Start Date:** 2026-08-24  
**Target Completion:** 2026-08-29 (5 days)  
**Depends On:** P0-01 (Routing) ✅, P0-02 (Context Schema) ✅  

---

## Executive Summary

**Problem:** Different projects have different rigor needs. A startup MVP doesn't need the same documentation as a healthcare system.
- **Lightweight:** Minimal artifacts, fast iteration, acceptable risk
- **Standard:** Balanced artifacts, production-ready, medium rigor
- **High-Rigor:** Extensive documentation, compliance-ready, maximum rigor

**Solution:** Define three rigor profiles that specify:
1. Required artifacts per work item type
2. Required skill sequence per phase
3. Verification/approval gates
4. How routing changes per profile

**Outcome:** Teams can choose rigor level upfront. Routing automatically enforces profile requirements (Gate 4 checks per-profile artifacts).

---

## 1. Design Rationale

### Why Rigor Profiles Matter

**Without profiles:**
```
Project A (startup): Blocked waiting for 50-page architecture review
Project B (healthcare): Missing compliance check; shipped insecure
Project C (mid-market): Over-documenting; slow iteration
→ No one-size-fits-all approach works
```

**With profiles:**
```
Project A chooses "Lightweight"
├─ Required: requirement + acceptance criteria
├─ Skip: full specification, architecture review, compliance check
├─ Result: Fast iteration, acceptable risk

Project B chooses "High-Rigor"
├─ Required: requirement + spec + architecture + compliance + approval
├─ Includes: security review, risk assessment
├─ Result: Slow but comprehensive

Project C chooses "Standard"
├─ Required: requirement + specification
├─ Includes: verification
├─ Skip: optional reviews
├─ Result: Balanced
```

### Design Constraints

1. **Explicit:** Profile is mandatory during setup (no accidental mixing)
2. **Consistent:** Once chosen, all work items follow profile requirements
3. **Auditable:** Can see which profile each project follows
4. **Flexible:** Can change profile mid-project (with impact analysis)
5. **Routing-Aware:** Gate 4 (Artifact Quality) checks per-profile artifacts

---

## 2. Three Rigor Profiles

### Profile 1: LIGHTWEIGHT

**Use Case:** Startup MVP, internal tools, prototypes, low-risk features

**Artifact Requirements:**

| Phase | Required | Optional | Skip |
|-------|----------|----------|------|
| Requirements | ✅ Requirement (FR/NFR) | ✅ Acceptance criteria | ❌ NFR formal specs |
| Design | ❌ Specification | ✅ Design doc (informal) | ❌ Architecture review |
| Implementation | ✅ Code + unit tests | ✅ Integration tests | ❌ Formal verification |
| Verification | ✅ Manual testing | ✅ E2E tests | ❌ Performance benchmarking |
| Approval | ✅ Dev lead review | ❌ | ❌ Compliance check |

**Skill Sequence:**
1. Requirement Analysis (optional detail level)
2. Specification Writer (optional; dev can use acceptance criteria)
3. Implementation (may write own tests)
4. Verification (light)
5. Code Review (peer only)

**Verification Gates:**
- Unit tests > 60% coverage (not 80%)
- Manual testing on main flows
- No security review required (use defaults)

**Timeline Impact:**
- Fast (days)
- Minimal documentation burden
- Risk: Missing edge cases, security issues

**Who Chooses This:** Startups, MVPs, internal tools, prototypes

---

### Profile 2: STANDARD

**Use Case:** Production systems, mid-market products, balanced rigor

**Artifact Requirements:**

| Phase | Required | Optional | Skip |
|-------|----------|----------|------|
| Requirements | ✅ Requirement + NFR | ✅ Risk assessment | ❌ Stakeholder sign-off |
| Design | ✅ Specification | ✅ Architecture diagram | ❌ Formal compliance review |
| Implementation | ✅ Code + tests | ✅ Performance profile | ❌ Formal verification proof |
| Verification | ✅ Comprehensive testing | ✅ Regression tests | ❌ Formal security audit |
| Approval | ✅ Tech lead + QA | ✅ | ❌ External audit |

**Skill Sequence:**
1. Requirement Analysis (full)
2. Specification Writer (required)
3. Implementation
4. Verification (comprehensive)
5. Code Review (tech lead + peer)
6. Regression Testing

**Verification Gates:**
- Unit tests > 80% coverage
- Integration tests passing
- Spec matches implementation
- No known critical/high security issues
- Performance within acceptable range

**Timeline Impact:**
- Medium (weeks)
- Standard documentation
- Risk: Acceptable, manageable

**Who Chooses This:** Most production products, mid-market, SaaS

---

### Profile 3: HIGH-RIGOR

**Use Case:** Healthcare, financial, safety-critical, compliance-heavy

**Artifact Requirements:**

| Phase | Required | Optional | Skip |
|-------|----------|----------|------|
| Requirements | ✅ Formal requirement | ✅ Formal approval | ✅ Compliance matrix |
| Design | ✅ Specification | ✅ Architecture review | ✅ Security design review |
| Implementation | ✅ Code + comprehensive tests | ✅ Formal code review | ✅ Traceability matrix |
| Verification | ✅ Formal verification | ✅ Security testing | ✅ Performance audit |
| Approval | ✅ Tech lead + Legal + Security | ✅ Compliance officer | ✅ External audit (if required) |

**Skill Sequence:**
1. Requirement Analysis (formal)
2. Specification Writer (formal, detailed)
3. Implementation (with traceability)
4. Verification (formal, with compliance checks)
5. Code Review (formal, documented)
6. Security Review
7. Compliance Review
8. External Audit (if required)

**Verification Gates:**
- Unit tests > 95% coverage
- All integration tests passing
- Security audit passing
- Compliance audit passing
- Formal verification proof (if applicable)
- Performance meets SLA (measured, documented)
- All requirements traceably implemented

**Timeline Impact:**
- Long (months)
- Extensive documentation
- Risk: Minimal, fully mitigated

**Who Chooses This:** Healthcare, financial, aviation, nuclear, medical devices

---

## 3. Profile Selection Matrix

### Decision Tree for Profile Selection

```
Question 1: What's the risk if something breaks?
├─ Acceptable loss: → Consider Lightweight
├─ Business impact: → Consider Standard
└─ Lives at risk / Legal liability: → Go to High-Rigor

Question 2: How fast do you need to iterate?
├─ < 1 week per feature: → Lightweight
├─ 1-4 weeks per feature: → Standard
└─ 1-3 months per feature: → High-Rigor

Question 3: Is this regulated/compliance-heavy?
├─ No: → Lightweight or Standard (based on risk)
├─ Yes, light regulation: → Standard
└─ Yes, heavy regulation: → High-Rigor

Question 4: Team experience?
├─ Early-stage team: → Standard (enforce good practices)
├─ Experienced team: → Can use Lightweight if risk acceptable
└─ Expert team on critical system: → High-Rigor

Outcome: Pick profile based on intersection of all factors
```

**Default:** Standard (safest choice if unsure)

---

## 4. Routing Integration (Gate 4: Artifact Quality)

### How Gate 4 Changes Per Profile

```python
def check_gate_4_artifact_quality(artifact, context_model):
    """
    Gate 4 behavior changes based on rigor_profile.
    """
    rigor_profile = context_model.get_project_config("rigor_profile")
    
    # Different artifact requirements per profile + artifact kind
    requirements = {
        "lightweight": {
            "work_item": ["requirement", "acceptance_criteria"],
            "requirement": [],
            "specification": ["requirement"],  # Optional but if exists, needs requirement
        },
        "standard": {
            "work_item": ["requirement", "specification"],
            "requirement": ["nfr"],  # At least one NFR
            "specification": ["requirement", "decision"],
        },
        "high_rigor": {
            "work_item": ["requirement", "specification", "verification", "risk_assessment"],
            "requirement": ["nfr", "stakeholder_approval"],
            "specification": ["requirement", "decision", "architecture_review", "security_review"],
        }
    }
    
    required_artifacts = requirements.get(rigor_profile, {}).get(artifact.kind, [])
    
    # Check if all required artifacts present
    for required_kind in required_artifacts:
        upstream = context_model.find_by_relationship(
            kind=required_kind,
            related_to=artifact.id
        )
        if not upstream:
            return {
                "gate": 4,
                "action_needed": True,
                "reason": "missing",
                "artifact_type": required_kind,
                "rigor_profile": rigor_profile
            }
    
    # Check validation status
    for required_kind in required_artifacts:
        upstream = context_model.find_by_relationship(kind=required_kind)
        if upstream and upstream.validation_status != "current":
            return {
                "gate": 4,
                "action_needed": True,
                "reason": "stale",
                "artifact_type": required_kind,
                "rigor_profile": rigor_profile
            }
    
    return {"gate": 4, "action_needed": False}
```

### Example: Same Work Item, Different Profiles

```yaml
Work Item: WI-042 "Implement JWT auth"

Lightweight Profile:
├─ Required: FR-001 (requirement), AC-001 (acceptance criteria)
├─ Check: Both exist? Both current?
├─ If missing SPEC-087: Proceed anyway (spec optional)
└─ Gate 4 result: PASS (proceed to implementation)

Standard Profile:
├─ Required: FR-001, SPEC-087, ADR-003
├─ Check: All exist? All current?
├─ If missing SPEC-087: FAIL (artifact_missing)
└─ Gate 4 result: BLOCKED (need specification first)

High-Rigor Profile:
├─ Required: FR-001, SPEC-087, ADR-003, SECURITY-REVIEW, RISK-ASSESSMENT
├─ Check: All exist? All current? All reviewed?
├─ If missing SECURITY-REVIEW: FAIL (artifact_missing)
└─ Gate 4 result: BLOCKED (need security review)
```

---

## 5. Profile-Specific Skill Sequences

### Skill Availability Per Profile

```yaml
Lightweight:
├─ Requirement Analysis (optional detail)
├─ Specification Writer (optional)
├─ Implementation (required)
├─ Verification (light, optional)
└─ Code Review (peer, required)

Standard:
├─ Requirement Analysis (required, full detail)
├─ Specification Writer (required)
├─ Implementation (required)
├─ Verification (required, comprehensive)
├─ Code Review (tech lead + peer)
├─ Regression Tester
└─ Performance Profiler (optional)

High-Rigor:
├─ Requirement Analysis (required, formal)
├─ Specification Writer (required, formal)
├─ Implementation (required, with traceability)
├─ Verification (required, formal)
├─ Code Review (required, formal and documented)
├─ Security Reviewer (required)
├─ Compliance Reviewer (required)
├─ Performance Auditor (required)
└─ External Auditor (optional, per compliance)
```

---

## 6. Profile Change During Project

### Changing Rigor Profile Mid-Project

**Scenario:** Start Lightweight, later discover healthcare requirements

```python
def change_rigor_profile(project_id, new_profile, context_model):
    """
    Change profile mid-project (risky but supported).
    """
    old_profile = context_model.get_project_config("rigor_profile")
    
    # Step 1: Mark all artifacts as "needs_recheck"
    # (Old profile doesn't have all required artifacts from new profile)
    all_artifacts = context_model.get_all_artifacts()
    for artifact in all_artifacts:
        if artifact.kind in ["requirement", "specification", "work_item"]:
            artifact.validation_status = "needs_recheck"
            artifact.profile_changed_from = old_profile
            artifact.profile_changed_to = new_profile
    
    # Step 2: Create escalation for impact analysis
    escalation = create_decision_escalation(
        decision_topic=f"Profile changed: {old_profile} → {new_profile}",
        affects=all_artifacts,
        options=[
            "Accept new profile; audit all artifacts",
            "Rollback to previous profile",
            "Mixed profile (high-rigor for critical path, standard for rest)"
        ]
    )
    
    # Step 3: Routing now enforces new profile
    # All "needs_recheck" artifacts will be revalidated against new requirements
    
    return escalation
```

**Impact Analysis:**
- Lightweight → Standard: Need specifications for all work items (effort increase)
- Lightweight → High-Rigor: Need specs + security reviews + compliance checks (major effort)
- Standard → High-Rigor: Need formal reviews + compliance (medium effort)
- High-Rigor → Standard/Lightweight: Usually not done (already meeting higher bar)

---

## 7. Artifact Matrix (Reference)

### Quick Lookup: Which Artifacts Are Required?

```
┌────────────────────────────────────────────────────────────────────┐
│                      RIGOR PROFILE ARTIFACT REQUIREMENTS             │
├────────────────────┬──────────────┬──────────────┬──────────────────┤
│ Artifact Type      │ Lightweight  │ Standard     │ High-Rigor       │
├────────────────────┼──────────────┼──────────────┼──────────────────┤
│ Requirement (FR)   │ ✅ Required  │ ✅ Required  │ ✅ Required      │
│ Requirement (NFR)  │ ❌ Optional  │ ✅ Required  │ ✅ Required      │
│ Acceptance Criteria│ ✅ Required  │ ✅ Required  │ ✅ Required      │
│ Specification      │ ❌ Optional  │ ✅ Required  │ ✅ Required      │
│ Architecture Review│ ❌ Skip      │ ❌ Optional  │ ✅ Required      │
│ Security Review    │ ❌ Skip      │ ❌ Optional  │ ✅ Required      │
│ Risk Assessment    │ ❌ Skip      │ ✅ Optional  │ ✅ Required      │
│ Verification Plan  │ ✅ Informal  │ ✅ Required  │ ✅ Required      │
│ Test Cases         │ ✅ Basic     │ ✅ Detailed  │ ✅ Comprehensive │
│ Code Review        │ ✅ Peer      │ ✅ Tech Lead │ ✅ Formal Board  │
│ Performance Audit  │ ❌ Skip      │ ❌ Optional  │ ✅ Required      │
│ Compliance Check   │ ❌ Skip      │ ❌ Skip      │ ✅ Required      │
│ External Audit     │ ❌ Skip      │ ❌ Skip      │ 🔶 Conditional  │
└────────────────────┴──────────────┴──────────────┴──────────────────┘
```

---

## 8. Acceptance Criteria

Rigor Profiles implementation is complete when:

- [ ] **AC-1:** Three profiles defined (Lightweight, Standard, High-Rigor)
- [ ] **AC-2:** Artifact requirements matrix per profile (what's required/optional/skip)
- [ ] **AC-3:** Skill sequence per profile documented (which skills in what order)
- [ ] **AC-4:** Verification gates per profile (coverage targets, approval process)
- [ ] **AC-5:** Profile selection decision tree (help teams choose)
- [ ] **AC-6:** Integration with routing Gate 4 (different artifacts checked per profile)
- [ ] **AC-7:** Profile change mechanism (mid-project change with impact analysis)
- [ ] **AC-8:** 3 worked examples (startup, mid-market, healthcare projects)
- [ ] **AC-9:** Timeline/effort estimates per profile
- [ ] **AC-10:** Default profile documented (Standard)

---

## 9. Decision Log

### Decision: Three Profiles (Not Configurable)

**Decision:** Fixed three profiles (Lightweight, Standard, High-Rigor). Not custom/configurable per project.

**Rationale:** Standardization. Three covers 95% of use cases. Custom profiles create inconsistency.

**Status:** LOCKED  
**Date:** 2026-08-24

---

### Decision: Mandatory Profile Selection at Setup

**Decision:** Projects must choose profile during creation. No default; explicit choice required.

**Rationale:** Prevents accidental mixing. Forces conscious rigor decision.

**Alternative:** Default to Standard — But this delays decision, causes rework later.

**Status:** LOCKED  
**Date:** 2026-08-24

---

## 10. Open Questions

1. **Can a team use mixed profile?** (High-rigor for auth, Lightweight for admin UI?)
2. **What's the cost (hours) difference between profiles?** (Need to estimate)
3. **Can teams extend profiles?** (Add custom artifacts beyond the profile?)
4. **Should regulatory/compliance certification vary per profile?** (Yes, per P0-08 decision)
5. **How do we measure profile compliance?** (Audit during P0-09)

---

## 11. Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-24 | Profile definitions + artifact matrix | TBD | In progress |
| 2026-08-25 | Skill sequences + verification gates | TBD | Not started |
| 2026-08-26 | Routing integration (Gate 4 per profile) | TBD | Not started |
| 2026-08-27 | Profile selection guide + change mechanism | TBD | Not started |
| 2026-08-28 | Worked examples (3 projects) | TBD | Not started |
| 2026-08-29 | Design complete + ready for P0-09 | TBD | Not started |

---

**P0-06 Design: Rigor Profiles — READY FOR TEAM EXECUTION**

Next: Assign Design Engineer #2 to complete by 2026-08-29.
