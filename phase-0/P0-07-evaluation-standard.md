# P0-07: Evaluation Standard

**Workstream:** P0-07  
**Title:** Skill Quality Evaluation Contract & Baseline  
**Status:** Design Phase  
**Design Lead:** TBD (Eval/Quality Lead)  
**Start Date:** 2026-08-17  
**Target Completion:** 2026-08-22 (5 days)  
**Depends On:** None (orthogonal to other workstreams)  

---

## Executive Summary

**Problem:** Phase 1 will implement skills that have variable quality. How do we measure whether a skill is working? What's the passing threshold? How do we detect regression?

**Solution:** Define an **evaluation contract**—a reusable specification that:
1. Defines what a skill should do (target capability)
2. Provides fixtures (example inputs)
3. Specifies expected output properties
4. Defines forbidden behaviors
5. Establishes scoring dimensions (e.g., precision, completeness, latency)
6. Sets passing thresholds (e.g., 90% precision)
7. Includes baseline comparison (vs. no-skill agent, vs. previous version)

**Outcome:** Skill quality is measurable, comparable, and regression-detectable.

---

## 1. Design Rationale

### Why Evaluation Contract Matters

**Without it:**
- Team implements Skill-A, tests informally, "seems good"
- Later, Skill-A causes issues; was it always wrong or did something regress?
- Next team implements Skill-B; how do we know it's better than Skill-A?
- No way to measure: "Is this skill worth maintaining?"

**With it:**
- Skill-A has a contract: "90% precision on requirement analysis"
- Contract specifies: 20 test cases, scoring method, pass/fail threshold
- Baseline run: Skill-A scores 92% (passes)
- Six months later: Skill-A scores 85% (regression detected)
- Team investigates: PR-xyz caused regression → revert or fix
- New Skill-B implementation: 94% on same 20 test cases (measurably better)

### Evaluation as Product Requirement

From PRD Section 20.3-20.4:
- Skills must be verifiable
- Verification must be repeatable
- Baseline must exist for comparison

**This workstream turns those requirements into concrete contracts.**

### Three Layers of Evaluation

1. **Unit Evaluation** — Does this skill work on simple cases?
   - Contracts: 1 per skill
   - Scope: Single skill in isolation
   - Example: "Routing skill can evaluate next step for 30 artifact types"

2. **Integration Evaluation** — Do multiple skills work together?
   - Contracts: 1 per skill combination
   - Scope: Multi-skill workflows
   - Example: "Requirement → Specification → Implementation pipeline"

3. **End-to-End Evaluation** — Can we ship a full feature?
   - Contracts: 1 per profile + scenario
   - Scope: Full project lifecycle
   - Example: "Greenfield project from vague idea to production code"

**P0-07 focuses on Unit + Integration layers. P0-09 (Lifecycle Validation) uses End-to-End contracts.**

---

## 2. Evaluation Contract Format (JSON Schema)

### Top-Level Structure

```json
{
  "contract_id": "EVAL-ROUTING-001",
  "contract_version": "1.0.0",
  "skill": "routing",
  "skill_version_tested": "1.0.0",
  "date_created": "2026-08-17",
  "date_last_run": "2026-08-17",
  
  "metadata": {
    "title": "Routing Precedence: Simple Artifact Evaluation",
    "description": "Verify routing can evaluate next step for 30 artifact types with 95% accuracy",
    "category": "unit",
    "priority": "P0",
    "owner": "Eval/Quality Lead"
  },
  
  "target_capability": {
    "description": "Given artifact with state + context, skill outputs correct next routing decision",
    "preconditions": [
      "Artifact exists with id, kind, status",
      "Context model includes decision_escalation, validation_status, dependencies",
      "Skill has access to P0-02 schema"
    ],
    "postconditions": [
      "Routing decision produced (state + reason)",
      "Decision is deterministic (same input → same output)",
      "Decision is auditable (explains which gates fired)"
    ]
  },
  
  "scenarios": [
    {
      "scenario_id": "ROUTE-001",
      "name": "Blocker Decision Unresolved",
      "description": "Artifact has unresolved decision_escalation → should route to escalate",
      "inputs": { ... },
      "expected_output": { ... },
      "scoring": { ... }
    },
    // ... more scenarios
  ],
  
  "fixtures": {
    "artifact_templates": [ ... ],
    "context_snapshots": [ ... ],
    "decision_escalation_examples": [ ... ]
  },
  
  "scoring": {
    "dimensions": [
      {
        "dimension": "accuracy",
        "description": "Does routing decision match expected?",
        "measurement": "percentage of test cases with correct decision",
        "weight": 0.6,
        "threshold": 0.95
      },
      {
        "dimension": "latency",
        "description": "How fast does routing evaluate?",
        "measurement": "milliseconds per evaluation",
        "weight": 0.2,
        "threshold": 100
      },
      {
        "dimension": "auditability",
        "description": "Can we explain why decision was made?",
        "measurement": "percentage of decisions with audit trail",
        "weight": 0.2,
        "threshold": 1.0
      }
    ],
    "pass_threshold": 0.85,
    "regression_tolerance": 0.05
  },
  
  "baseline": {
    "baseline_run_date": "2026-08-17",
    "baseline_vs_no_skill": {
      "description": "Compare against human manually choosing next step",
      "results": { ... }
    },
    "baseline_vs_previous_version": {
      "description": "Compare skill 1.0.0 vs. skill 0.9.0",
      "previous_version": "0.9.0",
      "results": { ... }
    }
  },
  
  "results": {
    "run_date": "2026-08-17T14:30:00Z",
    "skill_version": "1.0.0",
    "pass_fail": "PASS",
    "scores": {
      "accuracy": 0.96,
      "latency": 45,
      "auditability": 1.0,
      "overall": 0.92
    },
    "test_results": [ ... ]
  }
}
```

### Detailed Scenario Format

```json
{
  "scenario_id": "ROUTE-001",
  "name": "Blocker Decision Unresolved",
  "description": "Artifact WI-042 depends on unresolved decision_escalation → Route to Escalate & Wait",
  
  "inputs": {
    "artifact": {
      "id": "WI-042",
      "kind": "work_item",
      "status": "not_started",
      "summary": "Implement JWT auth",
      "depends_on": ["ESCA-001"]
    },
    "context": {
      "decision_escalations": [
        {
          "id": "ESCA-001",
          "status": "unresolved",
          "decision": "What auth scheme? OAuth? JWT? Session?",
          "affects": ["WI-042"]
        }
      ]
    }
  },
  
  "expected_output": {
    "routing_decision": "awaiting_decision",
    "reason": "Blocking decision ESCA-001 is unresolved; cannot proceed",
    "blocked_on": "ESCA-001",
    "action": "Escalate to authority",
    "resume_condition": "decision_escalation.status = resolved"
  },
  
  "forbidden_behaviors": [
    "Do NOT proceed with implementation despite unresolved decision",
    "Do NOT guess auth scheme",
    "Do NOT create decision_escalation instead of using existing ESCA-001"
  ],
  
  "scoring": {
    "criteria": [
      {
        "criterion": "Correct routing state",
        "points": 40,
        "verification": "Output.routing_decision == expected_output.routing_decision"
      },
      {
        "criterion": "Correct reason",
        "points": 30,
        "verification": "Output.reason mentions decision_escalation"
      },
      {
        "criterion": "Auditable (explains blocking decision)",
        "points": 20,
        "verification": "Output.blocked_on and Output.resume_condition present"
      },
      {
        "criterion": "Latency < 100ms",
        "points": 10,
        "verification": "Elapsed time < 100ms"
      }
    ],
    "total_points": 100
  }
}
```

### Scoring Aggregation

```
For 30 test scenarios:

Accuracy Score = (# correct routing decisions / 30) × 100
Latency Score = (# scenarios < 100ms / 30) × 100
Auditability Score = (# scenarios with audit trail / 30) × 100

Weighted Score = (0.6 × Accuracy) + (0.2 × Latency) + (0.2 × Auditability)

Pass Condition: Weighted Score >= 85% (threshold)
Regression Alert: Score dropped > 5% from baseline
```

---

## 3. Baseline Comparison

### No-Skill Baseline: Human Choice

**Scenario:** Replace skill with human making same routing decision.

**Method:**
1. Provide human with artifact + context (same inputs as skill)
2. Ask: "What's the next step? Why?"
3. Record: Which gate was most decisive? How long did it take?
4. Measure: Accuracy (does human choice match expected?), Latency (how long?)

**Example Results:**
```
Human No-Skill Baseline for Routing:
├─ Accuracy: 78% (makes mistakes on complex scenarios)
├─ Latency: 2-5 minutes per decision
└─ Auditability: 65% (explanations are vague)

Skill 1.0.0 Baseline (vs. no-skill):
├─ Accuracy: 96% (+18 percentage points)
├─ Latency: 45ms (-99.97% improvement)
├─ Auditability: 100% (+35 percentage points)
└─ Verdict: Skill is significantly better
```

### Previous Version Baseline

**Scenario:** Compare current skill to previous release.

**Method:**
1. Get previous skill version (e.g., 0.9.0)
2. Run same 30 test scenarios against both
3. Compare scores dimension-by-dimension

**Example Results:**
```
Skill 0.9.0 (Previous):
├─ Accuracy: 92%
├─ Latency: 120ms
└─ Auditability: 85%

Skill 1.0.0 (Current):
├─ Accuracy: 96% (↑ 4pp)
├─ Latency: 45ms (↓ 62.5%)
└─ Auditability: 100% (↑ 15pp)

Regression Check: PASS (no regression; improvements across board)
```

---

## 4. Example Evaluation Contracts

### Example 1: Routing Skill (Unit Evaluation)

**Contract ID:** EVAL-ROUTING-001  
**Skill:** Routing (from P0-01)  
**Test Scenarios:** 30 (covering all 7 gates)

| Gate | Scenarios | Example |
|------|-----------|---------|
| Gate 1: Blocking Decision | 5 | Unresolved decision, resolved decision, multiple decisions |
| Gate 2: Authority | 4 | Authority required, authority present, mixed |
| Gate 3: Uncertainty | 5 | Spike active, spike complete, no spike needed |
| Gate 4: Artifacts | 5 | Missing requirement, stale spec, all artifacts valid |
| Gate 5: Upstream | 3 | Upstream complete, upstream blocked, no upstream |
| Gate 6: Risk | 2 | Active risk blocks, risk mitigated |
| Gate 7: Ready | 1 | All gates pass → proceed |

**Scoring:**
- Accuracy: 95% (correct routing decision)
- Latency: 100ms (evaluation time)
- Auditability: 100% (explains which gate fired)
- Overall: 95% (pass threshold: 85%)

**Baseline Comparison:**
- vs. no-skill human: +18pp accuracy, -99.97% latency
- vs. Routing 0.9.0: +4pp accuracy, -62.5% latency

---

### Example 2: Requirement Analysis Skill (Unit Evaluation)

**Contract ID:** EVAL-REQANALYSIS-001  
**Skill:** Requirement Analysis (Phase 1 implementation)  
**Test Scenarios:** 20 (covering common requirement patterns)

| Scenario Type | Count | Example |
|---|---|---|
| Complete requirement | 5 | Well-formed FR with acceptance criteria |
| Ambiguous requirement | 5 | Vague goal; skill should identify ambiguities |
| Conflicting requirements | 3 | Two FRs contradict each other |
| Missing NFRs | 3 | Functional requirement without performance NFR |
| Poorly scoped requirement | 4 | Requirement too big or too small |

**Scoring Dimensions:**
1. **Precision** (60% weight): "If skill flags ambiguity, is it real?" (Target: 92%)
2. **Completeness** (20% weight): "Did skill find all ambiguities?" (Target: 85%)
3. **Actionability** (20% weight): "Does skill suggest concrete next steps?" (Target: 90%)
4. **Latency** (10% weight, bonus): Analysis time < 500ms

**Pass Threshold:** 87%

---

### Example 3: Integration Contract: Requirement → Specification

**Contract ID:** EVAL-INT-REQTOSPEC-001  
**Skills Tested:** Requirement Analysis + Specification Writer  
**Test Scenarios:** 10 (full workflows)

| Scenario | Input | Expected Output |
|---|---|---|
| Complete requirement | FR-001 "User auth" | SPEC-001 "JWT implementation" |
| Ambiguous requirement | FR-002 "Fast login" | Skill creates decision_escalation "What's acceptable latency?" |
| Conflict detected | FR-003 + FR-004 contradict | Both marked in relationship.contradicts |

**Scoring:**
- **End-to-end correctness** (50%): Specification matches requirement intent
- **Traceability** (30%): Specification correctly references requirement
- **Escalations handled** (20%): Ambiguities properly escalated (not ignored)

**Pass Threshold:** 90%

---

## 5. Test Fixture Format

### Artifact Templates (Reusable Test Data)

```json
{
  "fixture_type": "artifact_template",
  "templates": [
    {
      "name": "simple_requirement",
      "kind": "requirement",
      "template": {
        "id": "FR-{{NUM}}",
        "summary": "User can {{ACTION}}",
        "description": "Users want to {{ACTION}} to {{BENEFIT}}",
        "acceptance_criteria": ["Criterion 1", "Criterion 2"],
        "authority": "product_owner"
      }
    },
    {
      "name": "ambiguous_requirement",
      "kind": "requirement",
      "template": {
        "id": "FR-{{NUM}}",
        "summary": "System should be {{ADJECTIVE}}",
        "description": "We need better {{NOUN}}",
        "acceptance_criteria": []  // Missing criteria!
      }
    }
  ]
}
```

### Context Snapshots (Reusable Context States)

```json
{
  "fixture_type": "context_snapshot",
  "snapshots": [
    {
      "name": "greenfield_project",
      "description": "Fresh project; no artifacts yet",
      "requirements": [],
      "decisions": [],
      "decision_escalations": [],
      "work_items": [],
      "verifications": []
    },
    {
      "name": "mid_implementation",
      "description": "Project with some work done, some decisions open",
      "requirements": [
        { "id": "FR-001", "status": "verified" },
        { "id": "FR-002", "status": "approved", "validation_status": "current" }
      ],
      "decision_escalations": [
        { "id": "ESCA-001", "status": "unresolved", "affects": ["WI-042"] }
      ],
      "work_items": [
        { "id": "WI-001", "status": "complete" }
      ]
    }
  ]
}
```

---

## 6. Contract Execution (How Teams Use This)

### Phase 1 Team: When Implementing Skill-A

```
1. Read evaluation contract EVAL-SKILL-A-001
   ├─ Understand target capability
   ├─ Review 20 test scenarios
   ├─ See expected outputs
   └─ Understand pass threshold (87%)

2. Implement Skill-A

3. Run contract tests locally
   ├─ Feed each scenario to Skill-A
   ├─ Compare output vs. expected_output
   ├─ Score each scenario
   └─ Aggregate: Overall score = 91% ✅ PASS

4. Compare against baselines
   ├─ vs. human: +15pp accuracy (good!)
   ├─ vs. Skill-A 1.0.0: No regression (good!)
   └─ Verdict: Ready to ship

5. Save results to contract.results
   ├─ Timestamp: 2026-09-01T10:30:00Z
   ├─ Scores: { accuracy: 0.93, ... }
   ├─ Test details: [passing 18/20 scenarios]
   └─ Baseline comparison saved
```

### Maintenance: Regression Detection

```
6 months later (2027-02-01):

1. Run same contract tests again
   └─ Score: 82% (DOWN from 91% ↓ 9pp)

2. Regression detected!
   └─ Alert: Skill-A regressed beyond 5% tolerance

3. Investigation:
   ├─ Git log: PR-xyz merged 2 weeks ago
   ├─ PR-xyz changed routing logic
   └─ PR-xyz broke 3 test scenarios

4. Options:
   ├─ Revert PR-xyz
   ├─ Fix Skill-A to handle PR-xyz scenario
   └─ Update contract if requirement changed

5. Re-run contract
   └─ New score: 91% (fixed!)
```

---

## 7. Evaluation Schedule

### Phase 0 (Design)
- Define evaluation contract format
- Define scoring dimensions + thresholds
- Create 2-3 example contracts (Routing, Requirement Analysis, Integration)
- Define baseline methodology

### Phase 1 (Implementation)
- Each skill gets evaluation contract
- Baseline runs created (vs. no-skill, vs. previous version)
- Team passes tests before marking "complete"

### Phase 1+Maintenance (Operations)
- Regression tests run on schedule (weekly? monthly?)
- Alerts for scores dropping below threshold
- Historical tracking (plot score over time)

---

## 8. Acceptance Criteria

Evaluation Standard is complete when:

- [ ] **AC-1:** Evaluation contract JSON schema defined + documented
- [ ] **AC-2:** 3 example contracts created (Routing, Requirement Analysis, Integration)
- [ ] **AC-3:** Each example has 20-30 test scenarios with expected outputs
- [ ] **AC-4:** Scoring system defined (dimensions, weights, thresholds)
- [ ] **AC-5:** Baseline methodology defined (vs. no-skill, vs. previous version)
- [ ] **AC-6:** Test fixture format defined (artifact templates, context snapshots)
- [ ] **AC-7:** Regression detection defined (tolerance, alert policy)
- [ ] **AC-8:** Contract execution workflow documented (how teams run tests)
- [ ] **AC-9:** Historical tracking format defined (how scores are recorded over time)
- [ ] **AC-10:** Pass threshold for Phase 1 contracts determined (e.g., 85%, 90%, 95%)

---

## 9. Decision Log

### Decision: Weighted Scoring by Dimension (Not Single Overall Score)

**Decision:** Evaluate skills across multiple dimensions (accuracy, latency, auditability) with individual thresholds + weights for overall score.

**Rationale:**
- Single number (e.g., "90%") hides what's actually good/bad
- Weighted dimensions let us say: "Accuracy must be 95%, but latency can be more flexible"
- Different stakeholders care about different dimensions (user cares about accuracy; ops cares about latency)

**Status:** LOCKED  
**Date:** 2026-08-17

---

### Decision: Baseline Comparison vs. No-Skill + Previous Version

**Decision:** Every contract includes two baselines:
1. Human making same decision (no-skill)
2. Previous skill version (regression check)

**Rationale:**
- No-skill baseline answers: "Is this skill useful at all?" (should be YES)
- Previous version baseline answers: "Did we regress?" (should be NO)
- Together: Skills must be both useful AND not regressing

**Status:** LOCKED  
**Date:** 2026-08-17

---

### Decision: Regression Tolerance = 5% (Configurable per Dimension)

**Decision:** Skill regression alert triggers if score drops > 5% from baseline.

**Rationale:**
- 5% allows for noise (small variations in test execution)
- 5% is significant enough to warrant investigation
- Can be tuned per dimension (e.g., accuracy ≤ 3%, latency ≤ 10%)

**Depends On:** Phase 1 team feedback  
**Status:** PENDING  
**Date:** TBD

---

### Decision: Pass Threshold by Profile (Not Universal)

**Decision:** Passing threshold varies by skill priority + domain:
- P0 foundational skills (routing, context): 95%
- P1 core skills (requirement analysis, specs): 90%
- P2 nice-to-have skills: 85%

**Rationale:**
- Routing must be highly reliable (affects all downstream work)
- Requirement analysis can be more forgiving (human review catches errors)
- Optional skills have lower bar

**Depends On:** Phase 1 task prioritization  
**Status:** PENDING  
**Date:** TBD

---

## 10. Open Questions

1. **How often should regression tests run?** Weekly? Monthly? On every commit?
2. **Should evaluation be automated or manual?** (Likely hybrid)
3. **Who owns running evaluation tests?** QA team? Skill maintainers?
4. **Should evaluation results be visible to users?** (Transparency vs. liability)
5. **Can skills have time-dependent contracts?** (E.g., "faster over time as model warms up")

---

## 11. Next Documents

After P0-07 complete, P0-09 will use evaluation contracts to validate full lifecycle:
- **P0-09:** Integrated Lifecycle Validation
  - Run 6 scenarios through all 8 designs
  - Each scenario will have its own evaluation contract
  - Scenarios: greenfield, brownfield, interrupted, conflicts, staleness, lightweight

---

## Timeline

| Date | Task | Owner | Status |
|------|------|-------|--------|
| 2026-08-17 | Design contract format + scoring | TBD | In progress |
| 2026-08-19 | Create 3 example contracts | TBD | Not started |
| 2026-08-20 | Define test fixtures + baselines | TBD | Not started |
| 2026-08-21 | Workflow + Phase 1 integration | TBD | Not started |
| 2026-08-22 | Design complete + ready for Phase 1 | TBD | Not started |

---

**P0-07 Design: Evaluation Standard — READY FOR TEAM EXECUTION**

Next: Assign Eval/Quality Lead to complete by 2026-08-22.
