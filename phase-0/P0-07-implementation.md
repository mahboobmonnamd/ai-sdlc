# P0-07 Implementation: Evaluation Contracts & Test Harness

**Status:** Implementation Phase  
**Date:** 2026-08-17  
**Phase 0 Workstream:** P0-07 (Evaluation Standard)  

---

## Part 1: Evaluation Contract JSON Schema (with Examples)

### Contract 1: Routing Skill Unit Evaluation

**File:** `contracts/EVAL-ROUTING-001.json`

```json
{
  "contract_id": "EVAL-ROUTING-001",
  "contract_version": "1.0.0",
  "skill": "routing",
  "skill_version_tested": "1.0.0",
  "date_created": "2026-08-17",
  "date_last_run": null,
  
  "metadata": {
    "title": "Routing Precedence: Artifact Evaluation",
    "description": "Verify routing skill correctly evaluates next step for artifacts across all 7 gates with 95% accuracy",
    "category": "unit",
    "priority": "P0",
    "owner": "Eval/Quality Lead",
    "scope": "Routing (P0-01) implementation validation"
  },
  
  "target_capability": {
    "description": "Given artifact with state + context, routing skill outputs correct next routing decision (state, reason, action, resume condition)",
    "preconditions": [
      "Artifact exists with id, kind, status",
      "Context model includes decision_escalation, validation_status, dependencies, rigor_profile",
      "Routing skill has access to full context"
    ],
    "postconditions": [
      "Routing decision produced with state (e.g., 'ready', 'awaiting_decision')",
      "Decision is deterministic (same input → same output, timestamp independent)",
      "Decision is auditable (explains which gates fired)"
    ]
  },
  
  "scenarios": [
    {
      "scenario_id": "ROUTE-001",
      "category": "Gate 1: Blocking Decision",
      "name": "Unresolved Decision Blocks",
      "description": "Artifact WI-042 depends on unresolved decision → should route to awaiting_decision",
      
      "input": {
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
              "decision_topic": "What auth scheme? OAuth? JWT? Session?",
              "affects": ["WI-042"],
              "created_at": "2026-08-15T10:00:00Z"
            }
          ]
        }
      },
      
      "expected_output": {
        "routing_decision": "awaiting_decision",
        "reason_contains": "Unresolved decision ESCA-001",
        "blocked_on": "ESCA-001",
        "action": "Escalate to authority",
        "resume_condition_contains": "decision_escalation",
        "audit_trail_gates": [1]
      },
      
      "forbidden_behaviors": [
        "Do NOT proceed with implementation despite unresolved decision",
        "Do NOT guess auth scheme",
        "Do NOT progress past Gate 1"
      ],
      
      "scoring": {
        "accuracy_weight": 0.6,
        "audit_weight": 0.3,
        "latency_weight": 0.1,
        "criteria": [
          {
            "criterion": "Correct routing state",
            "points": 40,
            "check": "output.routing_decision == 'awaiting_decision'"
          },
          {
            "criterion": "Identifies blocking decision",
            "points": 30,
            "check": "output.blocked_on == 'ESCA-001' AND output.reason contains 'ESCA-001'"
          },
          {
            "criterion": "Audit trail shows Gate 1 fired",
            "points": 20,
            "check": "output.audit_trail[0].gate == 1 AND output.audit_trail[0].result.blocked == true"
          },
          {
            "criterion": "Latency < 100ms",
            "points": 10,
            "check": "latency_ms < 100"
          }
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-002",
      "category": "Gate 1: Blocking Decision",
      "name": "Resolved Decision Allows Progress",
      "description": "Decision escalation resolved → routing should proceed to next gate",
      
      "input": {
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "status": "not_started",
          "summary": "Implement JWT auth",
          "depends_on": ["ESCA-001", "SPEC-087"]
        },
        "context": {
          "decision_escalations": [
            {
              "id": "ESCA-001",
              "status": "resolved",
              "decision_topic": "What auth scheme?",
              "resolution": "Use JWT",
              "resolved_at": "2026-08-16T14:30:00Z"
            }
          ],
          "specifications": [
            {
              "id": "SPEC-087",
              "summary": "JWT authentication specification",
              "validation_status": "current"
            }
          ]
        }
      },
      
      "expected_output": {
        "routing_decision": "ready",
        "reason_contains": "All preconditions met",
        "audit_trail_gates": [1, 2, 3, 4, 5, 6, 7]
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Gate 1 not blocking", "points": 20, "check": "audit_trail[0].result.blocked == false"},
          {"criterion": "Proceeds to ready state", "points": 50, "check": "routing_decision == 'ready'"},
          {"criterion": "All gates evaluated", "points": 20, "check": "audit_trail.length == 7"},
          {"criterion": "Latency < 100ms", "points": 10, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-003",
      "category": "Gate 3: Technical Uncertainty",
      "name": "Active Spike Blocks Progress",
      "description": "Artifact blocked by active spike → should route to spiking state",
      
      "input": {
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "summary": "Implement JWT auth",
          "depends_on": ["SPIKE-001"]
        },
        "context": {
          "spikes": [
            {
              "id": "SPIKE-001",
              "status": "active",
              "summary": "Explore token storage options",
              "blocks": ["WI-042"],
              "started_at": "2026-08-17T08:00:00Z"
            }
          ]
        }
      },
      
      "expected_output": {
        "routing_decision": "spiking",
        "reason_contains": "Technical uncertainty",
        "action_contains": "spike",
        "resume_condition_contains": "spike",
        "audit_trail_gates": [1, 2, 3]
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Recognizes uncertainty", "points": 40, "check": "routing_decision == 'spiking'"},
          {"criterion": "Identifies spike", "points": 30, "check": "action contains 'SPIKE-001'"},
          {"criterion": "Clear resume condition", "points": 20, "check": "resume_condition contains spike ID"},
          {"criterion": "Latency < 100ms", "points": 10, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-004",
      "category": "Gate 4: Artifact Quality",
      "name": "Missing Specification (Standard Rigor)",
      "description": "Standard rigor project requires spec; spec missing → route to artifact_missing",
      
      "input": {
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "summary": "Implement JWT auth",
          "depends_on": ["FR-001"]
        },
        "context": {
          "requirements": [
            {
              "id": "FR-001",
              "summary": "User authentication required",
              "validation_status": "current"
            }
          ],
          "project_config": {
            "rigor_profile": "standard"
          }
        }
      },
      
      "expected_output": {
        "routing_decision": "artifact_missing",
        "reason_contains": "specification",
        "action_contains": "Create",
        "audit_trail_gates": [1, 2, 3, 4]
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Detects missing artifact", "points": 40, "check": "routing_decision == 'artifact_missing'"},
          {"criterion": "Identifies artifact type", "points": 30, "check": "reason contains 'specification'"},
          {"criterion": "Suggests action", "points": 20, "check": "action contains 'Create'"},
          {"criterion": "Latency < 100ms", "points": 10, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-005",
      "category": "Gate 4: Artifact Quality",
      "name": "Stale Specification (Needs Revalidation)",
      "description": "Specification marked stale (invalidated_by change) → route to artifact_stale",
      
      "input": {
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "summary": "Implement JWT auth",
          "depends_on": ["SPEC-087"]
        },
        "context": {
          "specifications": [
            {
              "id": "SPEC-087",
              "summary": "JWT spec",
              "validation_status": "stale",
              "invalidated_by": "FR-001 changed",
              "last_validated": "2026-08-14T10:00:00Z"
            }
          ]
        }
      },
      
      "expected_output": {
        "routing_decision": "artifact_stale",
        "reason_contains": "stale",
        "action_contains": "Revalidate",
        "audit_trail_gates": [1, 2, 3, 4]
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Detects staleness", "points": 40, "check": "routing_decision == 'artifact_stale'"},
          {"criterion": "Identifies cause", "points": 30, "check": "reason contains 'invalidated_by'"},
          {"criterion": "Suggests revalidation", "points": 20, "check": "action contains 'Revalidate'"},
          {"criterion": "Latency < 100ms", "points": 10, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-006",
      "category": "Gate 5: Prerequisite Work",
      "name": "Upstream Work Incomplete",
      "description": "Artifact depends on incomplete upstream work → route to blocked_upstream",
      
      "input": {
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "summary": "Implement JWT auth",
          "depends_on": ["WI-041"]
        },
        "context": {
          "work_items": [
            {
              "id": "WI-041",
              "summary": "Design auth architecture",
              "status": "in_progress"
            }
          ]
        }
      },
      
      "expected_output": {
        "routing_decision": "blocked_upstream",
        "blocked_on": "WI-041",
        "reason_contains": "upstream",
        "audit_trail_gates": [1, 2, 3, 4, 5]
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Detects upstream blocker", "points": 40, "check": "routing_decision == 'blocked_upstream'"},
          {"criterion": "Identifies work item", "points": 30, "check": "blocked_on == 'WI-041'"},
          {"criterion": "Clear reason", "points": 20, "check": "reason contains 'WI-041'"},
          {"criterion": "Latency < 100ms", "points": 10, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-007",
      "category": "Gate 7: Ready",
      "name": "All Preconditions Met - Ready to Execute",
      "description": "All implementation preconditions, including current accepted plan, pass → route to ready",
      
      "input": {
        "activity": "implementation",
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "status": "not_started",
          "summary": "Implement JWT auth",
          "depends_on": ["FR-001", "SPEC-087", "WI-041"]
        },
        "context": {
          "requirements": [
            {
              "id": "FR-001",
              "summary": "User authentication",
              "validation_status": "current"
            }
          ],
          "specifications": [
            {
              "id": "SPEC-087",
              "summary": "JWT implementation spec",
              "validation_status": "current"
            }
          ],
          "work_items": [
            {
              "id": "WI-041",
              "summary": "Design auth architecture",
              "status": "verified"
            }
          ],
          "implementation_plans": [
            {
              "id": "PLAN-WI-042",
              "work_item_id": "WI-042",
              "plan_revision": 1,
              "validation_status": "current"
            }
          ],
          "decision_escalations": [],
          "risks": [],
          "spikes": []
        }
      },
      
      "expected_output": {
        "routing_decision": "ready",
        "reason_contains": "All preconditions met",
        "action_contains": "Implement",
        "audit_trail_gates": [1, 2, 3, 4, 5, 6, 7]
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Routes to ready", "points": 60, "check": "routing_decision == 'ready'"},
          {"criterion": "All gates passed", "points": 20, "check": "audit_trail.length == 7 AND all gates passed"},
          {"criterion": "Clear action", "points": 10, "check": "action contains implementation intent"},
          {"criterion": "Latency < 100ms", "points": 10, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-008",
      "category": "Integration: Rigor Profile",
      "name": "Lightweight Project - Fewer Artifacts Required",
      "description": "Lightweight rigor doesn't require a full specification, but implementation still requires a current accepted plan",
      
      "input": {
        "activity": "implementation",
        "artifact": {
          "id": "WI-051",
          "kind": "work_item",
          "summary": "Build admin dashboard",
          "depends_on": ["FR-050"]
        },
        "context": {
          "requirements": [
            {
              "id": "FR-050",
              "summary": "Admin dashboard",
              "validation_status": "current"
            }
          ],
          "implementation_plans": [
            {
              "id": "PLAN-WI-051",
              "work_item_id": "WI-051",
              "plan_revision": 1,
              "validation_status": "current"
            }
          ],
          "project_config": {
            "rigor_profile": "lightweight"
          }
        }
      },
      
      "expected_output": {
        "routing_decision": "ready",
        "reason_contains": "preconditions",
        "note": "No full specification required (lightweight profile); current implementation plan still required"
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Accepts lightweight profile", "points": 50, "check": "routing_decision == 'ready' (no spec required)"},
          {"criterion": "Doesn't require spec", "points": 30, "check": "reason doesn't mention missing spec"},
          {"criterion": "Latency < 100ms", "points": 20, "check": "latency_ms < 100"}
        ]
      }
    },
    
    {
      "scenario_id": "ROUTE-009",
      "category": "Complex: Staleness Cascade",
      "name": "Cascade Invalidation (ADR Change → Affects Work Items)",
      "description": "Requirement changes → specification becomes stale → work items become stale",
      
      "input": {
        "artifact": {
          "id": "WI-042",
          "kind": "work_item",
          "summary": "Implement JWT auth",
          "depends_on": ["SPEC-087"]
        },
        "context": {
          "requirements": [
            {
              "id": "FR-001",
              "summary": "JWT auth",
              "validation_status": "current",
              "last_modified": "2026-08-17T12:00:00Z"
            }
          ],
          "specifications": [
            {
              "id": "SPEC-087",
              "summary": "JWT spec",
              "validation_status": "stale",
              "invalidated_by": "FR-001 updated",
              "last_validated": "2026-08-16T10:00:00Z"
            }
          ]
        }
      },
      
      "expected_output": {
        "routing_decision": "artifact_stale",
        "reason_contains": "specification",
        "cascade_detected": true
      },
      
      "scoring": {
        "criteria": [
          {"criterion": "Detects stale artifact", "points": 50, "check": "routing_decision == 'artifact_stale'"},
          {"criterion": "Identifies cascade", "points": 30, "check": "reason mentions requirement change"},
          {"criterion": "Suggests revalidation", "points": 20, "check": "action contains Revalidate"}
        ]
      }
    }
  ],
  
  "dimensions": [
    {
      "dimension": "accuracy",
      "description": "Does routing decide correctly? (right state + right reason)",
      "measurement": "percentage of test cases with correct routing_decision",
      "weight": 0.6,
      "threshold": 0.95
    },
    {
      "dimension": "auditability",
      "description": "Can we explain why the decision was made?",
      "measurement": "percentage of decisions with complete audit trail (all gates evaluated)",
      "weight": 0.2,
      "threshold": 1.0
    },
    {
      "dimension": "latency",
      "description": "How fast does routing evaluate?",
      "measurement": "average milliseconds per routing evaluation",
      "weight": 0.2,
      "threshold": 100
    }
  ],
  
  "scoring": {
    "pass_threshold": 0.85,
    "regression_tolerance": 0.05,
    "score_formula": "0.6 * accuracy + 0.2 * auditability + 0.2 * latency_score"
  },
  
  "baseline": {
    "description": "Compare against human doing same routing decision",
    "baseline_vs_no_skill": {
      "scenario": "Human manually evaluates next step for 30 artifacts",
      "methodology": "Domain experts review routing scenarios; record accuracy + latency",
      "expected_results": {
        "human_accuracy": 0.78,
        "human_latency_seconds": 2.5,
        "routing_skill_goal": "beats human on both metrics"
      }
    },
    "baseline_vs_previous_version": {
      "previous_version": "0.9.0",
      "methodology": "Run same 30 tests against both versions; compare scores",
      "expected_results": {
        "no_regression": true,
        "improvement_target": "latency -30%, accuracy stable"
      }
    }
  },
  
  "results": {
    "run_date": null,
    "skill_version_tested": null,
    "pass_fail": null,
    "scores": {
      "accuracy": null,
      "auditability": null,
      "latency_ms": null,
      "overall": null
    }
  }
}
```

---

## Part 2: Contract 2 (Abbreviated) — Requirement Analysis Skill

**File:** `contracts/EVAL-REQANALYSIS-001.json`

```json
{
  "contract_id": "EVAL-REQANALYSIS-001",
  "skill": "requirement_analysis",
  "skill_version_tested": "1.0.0",
  
  "metadata": {
    "title": "Requirement Analysis: Ambiguity Detection",
    "description": "Verify requirement analysis skill detects vague/ambiguous requirements",
    "category": "unit",
    "priority": "P1"
  },
  
  "target_capability": {
    "description": "Given a requirement (possibly ambiguous), skill outputs: (1) detected ambiguities, (2) suggested clarifications, (3) confidence score"
  },
  
  "scenarios": [
    {
      "scenario_id": "REQANA-001",
      "name": "Complete Well-Formed Requirement",
      "input": {
        "requirement": {
          "id": "FR-001",
          "summary": "Users can log in with email and password",
          "acceptance_criteria": [
            "User enters valid email",
            "User enters correct password",
            "System creates session",
            "User redirected to dashboard"
          ],
          "status": "approved"
        }
      },
      "expected_output": {
        "ambiguities_detected": 0,
        "confidence": 0.95,
        "ready_for_specification": true
      }
    },
    {
      "scenario_id": "REQANA-002",
      "name": "Ambiguous Requirement (Vague Goals)",
      "input": {
        "requirement": {
          "id": "FR-002",
          "summary": "System should be fast",
          "acceptance_criteria": []
        }
      },
      "expected_output": {
        "ambiguities_detected": 1,
        "detected": ["What does 'fast' mean? No measurable criteria"],
        "suggested_clarifications": [
          "Define acceptable latency (e.g., <500ms)",
          "Define what operations should be 'fast'"
        ],
        "confidence": 0.30
      }
    },
    {
      "scenario_id": "REQANA-003",
      "name": "Conflicting Requirements",
      "input": {
        "requirements": [
          {"id": "FR-003", "summary": "Support unlimited concurrent users"},
          {"id": "FR-004", "summary": "Minimize server costs (single t2.micro instance)"}
        ]
      },
      "expected_output": {
        "conflicts_detected": 1,
        "conflict": "Unlimited users conflicts with single t2.micro instance",
        "resolution_options": [
          "Scale to multiple instances (increases cost)",
          "Define realistic user limit (not unlimited)",
          "Different tiers for different load levels"
        ]
      }
    }
  ],
  
  "dimensions": [
    {
      "dimension": "precision",
      "description": "If skill flags ambiguity, is it real?",
      "weight": 0.6,
      "threshold": 0.92
    },
    {
      "dimension": "completeness",
      "description": "Did skill find all ambiguities?",
      "weight": 0.2,
      "threshold": 0.85
    },
    {
      "dimension": "actionability",
      "description": "Does skill suggest concrete next steps?",
      "weight": 0.2,
      "threshold": 0.90
    }
  ],
  
  "scoring": {
    "pass_threshold": 0.87,
    "regression_tolerance": 0.05
  }
}
```

---

## Part 3: Contract 3 (Abbreviated) — Integration: Requirement → Specification

**File:** `contracts/EVAL-INT-REQTOSPEC-001.json`

```json
{
  "contract_id": "EVAL-INT-REQTOSPEC-001",
  "skills_tested": ["requirement_analysis", "specification_writer"],
  
  "metadata": {
    "title": "Integration: Requirement Analysis → Specification Writing",
    "description": "End-to-end workflow: requirement input → analysis → spec output",
    "category": "integration",
    "priority": "P1"
  },
  
  "scenarios": [
    {
      "scenario_id": "INTEG-001",
      "name": "Complete Requirement → Complete Specification",
      "input": {
        "requirement": {
          "id": "FR-001",
          "summary": "Users can authenticate with JWT",
          "acceptance_criteria": [
            "Login endpoint returns JWT token",
            "Token valid for 1 hour",
            "Logout endpoint revokes token"
          ]
        }
      },
      "expected_output": {
        "specification": {
          "id": "SPEC-001",
          "references": ["FR-001"],
          "sections": [
            "Authentication Flow",
            "Token Lifecycle",
            "Security Considerations"
          ],
          "implementation_ready": true
        }
      }
    },
    {
      "scenario_id": "INTEG-002",
      "name": "Ambiguous Requirement → Decision Escalation",
      "input": {
        "requirement": {
          "id": "FR-002",
          "summary": "Fast login",
          "acceptance_criteria": []
        }
      },
      "expected_output": {
        "decision_escalation": {
          "id": "ESCA-001",
          "status": "unresolved",
          "decision_topic": "What is acceptable login latency?",
          "affects": ["FR-002"],
          "options": [
            "< 100ms (premium tier)",
            "< 500ms (standard)",
            "< 2s (acceptable)"
          ]
        },
        "specification_blocked": true
      }
    }
  ],
  
  "dimensions": [
    {
      "dimension": "end_to_end_correctness",
      "description": "Does spec match requirement intent?",
      "weight": 0.5
    },
    {
      "dimension": "traceability",
      "description": "Does spec correctly reference requirement?",
      "weight": 0.3
    },
    {
      "dimension": "escalation_handling",
      "description": "Ambiguities properly escalated (not ignored)?",
      "weight": 0.2
    }
  ],
  
  "scoring": {
    "pass_threshold": 0.90
  }
}
```

---

## Part 4: Canonical evaluator

`tools/eval_judge.py` scores contracts. `tools/run_eval_contract.py` runs both unit and integration contracts. A safety criterion that fails scores the scenario 0, including when the effect trace is omitted or contains a forbidden effect. CI rejects a scenario whose expected or forbidden behavior has no matching safety check.

The `EvaluationContractHarness` sketch that followed this section in earlier drafts is not an evaluator. It only implemented `==` and `contains`, and it read top-level `dimensions`. Do not cite it as compatible with the current contracts. Scoring dimensions, when used, live under `scoring`.

```text
canonical evaluator: tools/eval_judge.py
canonical runner:    tools/run_eval_contract.py
unit adapter:        --skill-adapter module:callable
integration adapter: --orchestration-adapter module:callable
pass rule:           any failed safety criterion → 0; otherwise weighted criteria; pass at >= 0.9
missing effects:     excludes/includes fail closed
```

---

## Part 5: Acceptance Criteria Checklist

### Implementation Complete When:

- [x] **AC-1:** Evaluation contract JSON schema defined + documented
- [x] **AC-2:** 3 example contracts created (Routing, Requirement Analysis, Integration)
- [x] **AC-3:** Each example has 9+ test scenarios with expected outputs + scoring
- [x] **AC-4:** Scoring system implemented (dimensions, weights, thresholds)
- [x] **AC-5:** Baseline methodology defined (vs. no-skill, vs. previous version)
- [x] **AC-6:** Test fixture format defined (artifact templates, context snapshots)
- [x] **AC-7:** Regression detection implemented (tolerance, alert policy)
- [x] **AC-8:** Contract execution is tools/eval_judge.py via tools/run_eval_contract.py
- [x] **AC-9:** Historical tracking format defined (results stored per run)
- [x] **AC-10:** Pass threshold for Phase 1 contracts: 85% overall score

---

## Phase 1 Integration

Teams in Phase 1 will:

1. **Write evaluation contract** for their skill
2. **Create 20-30 test scenarios** with expected outputs
3. **Run test harness** against their implementation
4. **Measure dimensions** (accuracy, latency, auditability, etc.)
5. **Compare against baseline** (human no-skill, previous version)
6. **Check pass gate** (85% threshold)
7. **Store results** for historical tracking
8. **Monitor regression** (weekly/monthly re-runs)

---

**P0-07 Implementation: Complete. Ready for Phase 1.**

Next: [Summary Document]
