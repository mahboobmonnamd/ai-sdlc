# P0-02 — Context Data Model Design

**Phase:** 0 (Architecture & Design)  
**Status:** Design Phase (IN PROGRESS)  
**Date Started:** 2026-08-17  
**Target:** Define canonical logical schema + authoritative serialization format

---

## 1. Design Rationale

### Why One Canonical Format

**Problem:** Maintaining parallel context.yaml and context.json creates divergence risk
```text
✗ context.yaml (last edited: commit abc123)
✗ context.json (last edited: commit def456)
Which is authoritative? What if they disagree?
```

**Solution:** Single canonical format with optional read-only interop
```text
✓ .sdlc/context/ (YAML, authoritative)
     ↓
  Canonical source of truth
     ↓
  ├─ Optional: JSON export for API tooling (regenerated from YAML)
  ├─ Optional: SQL views for querying (materialized from YAML)
  └─ Optional: GraphQL schema (derived read-only)
```

### Format Choice: YAML

**Criteria:**
| Criterion | YAML | JSON | SQLite |
|---|---|---|---|
| Human readability | ✅ Excellent | ⚠️ OK | ❌ Binary |
| Git-friendly (diffs) | ✅ Yes | ⚠️ Verbose | ❌ No |
| Schema flexibility | ✅ High | ✅ High | ⚠️ Fixed schema |
| No external deps | ✅ Yes | ✅ Yes | ⚠️ SQLite binary |
| Nested structures | ✅ Native | ✅ Native | ⚠️ Joins needed |
| Comments/annotations | ✅ Native | ❌ No | ⚠️ Metadata table |
| Project portability | ✅ Easy | ✅ Easy | ⚠️ Tools needed |

**Decision:** **YAML is authoritative.**

**Rationale:**
- Most human-readable for code review + git history
- Comments allow recording decisions/assumptions directly
- Nested nature matches entity relationships naturally
- Agents can read/edit directly with standard YAML libs
- Still JSON-interoperable for automation

---

## 2. Canonical Logical Data Model

### Core Entity Types

```yaml
# Entity: represents a thing that exists in project context
# Every entity has:
#   - id: stable identifier for relationships
#   - kind: entity type (requirement, decision, work_item, etc.)
#   - status: state (draft, proposed, accepted, stale, superseded, verified)
#   - summary: human-readable description
#   - created_at: ISO8601 timestamp
#   - source: what authoritative source created it
#   - authority: who can make decisions about it
#   - last_validated: when was source checked?
#   - relationships: links to other entities

# Relationship: connects two entities
# relationship(from_entity, type, to_entity)
# Examples:
#   requirement(FR-001) --requires--> feature(sign_in)
#   requirement(FR-001) --governed-by--> decision(ADR-003)
#   work_item(WI-042) --implements--> requirement(FR-001)
#   decision(ADR-005) --supersedes--> decision(ADR-002)
```

### Entity Kinds (Minimal Set for Phase 1)

| Kind | Example ID | Purpose | Authority |
|---|---|---|---|
| `requirement` | FR-001 | Product/functional requirement | Product owner |
| `nfr` | NFR-003 | Non-functional requirement | Product owner + architect |
| `decision` | ADR-005 | Architectural decision record | Architect |
| `specification` | SPEC-002 | Technical specification | Lead engineer |
| `spike` | SPIKE-012 | Technical investigation | Lead engineer |
| `spike_finding` | FINDING-012a | Result of spike investigation | Lead engineer |
| `work_item` | WI-042 | Implementation task/feature/bug | Dev team |
| `implementation_plan` | PLAN-WI-042 | Versioned plan for implementing one work item (proposed until accepted) | Dev/technical authority under project policy |
| `milestone` | M-001 | Release/feature grouping | Product owner |
| `verification` | VER-087 | Evidence item proving acceptance | QA/verification |
| `risk` | RISK-004 | Known risk or blocker | As appropriate |
| `handoff` | HO-020 | Session/developer handoff record | Handoff creator |
| `decision_escalation` | ESC-015 | Unresolved decision waiting for authority | Escalation owner |
| `component` | COMP-auth | Codebase component/module | Architecture |
| `context_fact` | FACT-003 | Derived observation from codebase | Setup/analysis |

### Minimal Required Fields (per Entity)

```yaml
entity:
  id: "FR-001"                          # Stable, globally unique within project
  kind: "requirement"                   # Entity type (from table above)
  status: "accepted"                    # draft|proposed|accepted|stale|superseded|verified|blocked
  
  # Human context
  summary: "User can sign in with email/password"
  description: |                        # Multi-line OK
    As a user, I want to sign in with email/password
    so that I can access my account securely.
  
  # Provenance (WHERE did this come from?)
  source:
    file: "docs/requirements.md"        # Authoritative source document
    line: 42                             # Line number in source
    commit: "abc123def456"              # Git commit where last validated
    
  # Authority (WHO can change this?)
  authority: "product_owner"            # Role/person who owns this entity
  
  # Validation (Is this current?)
  created_at: "2026-08-15T10:30:00Z"   # ISO8601
  last_validated: "2026-08-17T14:22:00Z"
  validation_status: "current"          # current|stale|needs_recheck
  
  # Relationships (HOW does this connect?)
  relationships:
    - target: "ADR-003"                 # ID of related entity
      type: "governed_by"               # Relationship type
      direction: "from"                 # Is this entity the "from" or "to"?
    - target: "WI-042"
      type: "implemented_by"
      direction: "to"
    
  # Staleness tracking (WHAT affects this?)
  depends_on:                           # If these change, revalidate this
    - "ADR-003"
    - "COMP-auth"
  affects:                              # If this changes, these become stale
    - "SPEC-002"
    - "WI-042"
    - "VER-087"
  
  # Metadata (Additional context)
  tags: ["authentication", "critical"]
  complexity: "medium"                  # lightweight|medium|heavy
  rigor_profile: "standard"             # lightweight|standard|high_rigor
```

### Relationship Types (Semantic)

```
# Structural relationships
requires        Entity A requires Entity B (FR → User Story)
implements      Entity A implements Entity B (WI → Requirement)
plans           Entity A is the implementation plan for Entity B (Plan → WI)
depends_on      Entity A depends on Entity B (WI/Plan → Spike/Spec/Decision)
blocks           Entity A is blocked by Entity B (WI blocked by Decision)
supersedes      Entity A replaces Entity B (ADR-005 supersedes ADR-002)

# Governance relationships
governed_by     Entity A is constrained by Entity B (Spec governed by ADR)
specified_by    Entity A is defined by Entity B (WI specified by Specification)
verified_by     Entity A is proven by Entity B (Requirement verified by Evidence)

# Composition relationships
part_of         Entity A is part of Entity B (WI part of Milestone)
contains        Entity A contains Entity B (Milestone contains WI)

# Consistency relationships
contradicts     Entity A conflicts with Entity B (Requirement contradicts Requirement)
related_to      Entity A is conceptually related to Entity B (For tagging)
```

---

## 3. Canonical YAML Serialization

### Implementation-plan identity

Implementation plans are durable derived entities, not transient agent reasoning. A plan must be resolvable later by readiness, implementation, review, and resumability.

```yaml
entity:
  id: "PLAN-WI-042"
  kind: "implementation_plan"
  status: "proposed"                    # proposed until technical authority accepts
  work_item_id: "WI-042"
  plan_revision: 3
  source:
    file: ".sdlc/context/implementation_plans.yaml"
    commit: "abc123def456"
  validation_status: "current"

  # Revisions whose change requires plan revalidation.
  governing_revisions:
    work_item_semantic: "WI-042@scope-7"
    specification: "SPEC-002@4"
    decisions:
      ADR-003: 2

  relationships:
    - target: "WI-042"
      type: "plans"
      direction: "from"

  depends_on:
    - "WI-042"
    - "SPEC-002"
    - "ADR-003"
```

`plan_id` is the entity `id`; `plan_revision` advances when plan content changes (proposal or refresh). New revisions are created as `proposed`. `governing_revisions` track planning-relevant semantic content, not ordinary coordination metadata: claim, assignee, workflow-status, or comment-only changes do not invalidate a plan unless they alter accepted scope, acceptance, dependencies, authority, or another planning input. A plan may remain readable for history after becoming stale, but readiness/implementation/review must not treat a stale or merely proposed plan as the accepted plan.

**Plan creation and plan acceptance are separate.** `implementation-planning` may create/refresh a `proposed` revision; only a project-defined technical-authority acceptance operation may mark that revision accepted and advance the work-item pointer.

The work item (or an equivalent project-owned registry) must also identify **which plan revision is currently accepted**, with acceptance evidence. A relationship to a plan entity is not enough when old revisions remain addressable, and a newly proposed revision must not self-advance this pointer.

```yaml
work_item:
  id: "WI-042"
  kind: "work_item"
  accepted_plan:
    work_item_id: "WI-042"
    plan_id: "PLAN-WI-042"
    plan_revision: 3
    accepted_by: "tech-lead@example.com"    # identity from a host principal
    authenticated_by: "host-session"        # must be listed in policy.authenticators
    authority_assertion: "session-accept-3"
    accepted_at: "2026-09-26T12:00:00Z"
    acceptance_source: "decision-record:ADR-accept-3"
    operation: "plan_acceptance"            # only accept_plan() may write this pointer
plans:
  PLAN-WI-042:
    revisions:
      3:
        id: "PLAN-WI-042"
        work_item_id: "WI-042"
        plan_revision: 3
        status: "accepted"
        accepted_revision: 3
        validation_status: "current"
```

`accepted_plan` is a protected pointer. Only `accept_plan()` in `tools/plan_acceptance.py` may write it. The host passes a principal `{identity, authenticator, assertion_id}` that its own session already authenticated. A bare email or other identity string is rejected. `identity` must be in `technical_authorities`, and `authenticator` must be in `authenticators`. The accepted body is stored at `(plan_id, plan_revision)` and must name the same work item. Verification reads that revision, not whatever object is currently stored under the plan id. Filling the fields from a planning skill is not acceptance. This follow-up adopts the schema `2.0.0` already recorded in this document, including the 1.x migration that refuses fabricated acceptance evidence. It does not add a general capability or trusted-principal system.

### Candidate lifecycle stage

When a merge candidate exists, its stage is durable project state, not session memory. Resume, consumer facades, and review routing read this record. If it is absent, reconstruct it using the rules in P0-05; do not assume `IN_REVIEW`.

```yaml
merge_candidate:
  id: "PR-99"
  work_item_id: "WI-042"          # null when lifecycle_work_item is NOT_APPLICABLE
  candidate_lifecycle_stage: "IMPLEMENTATION_IN_PROGRESS"  # or IN_REVIEW | UNKNOWN
  owner: "dev-a"                        # must match the active claim when a claim policy exists
  stage_set_by: "implementation"  # only implementation may transition the stage
  stage_set_at: "2026-09-26T12:00:00Z"
  stage_reason: "accepted scope still incomplete"
```

Transition authority:

- `implementation` sets `IMPLEMENTATION_IN_PROGRESS` when accepted scope is incomplete, including while CI fails or early comments exist.
- `implementation` sets `IN_REVIEW` only after accepted-scope implementation is complete.
- `pr-review` and `address-pr-review` must not promote an incomplete candidate to `IN_REVIEW`.

The storage representation must make every referenced `(plan_id, plan_revision)` **resolvable to immutable plan content**. Keeping only the latest mutable plan body is insufficient. A project may satisfy this with immutable revision records, an embedded revision history, or VCS-backed revision/source references, but consumers must be able to load the exact accepted revision without guessing from "latest".

### Directory Structure

```
project/
├── .sdlc/
│   ├── context/                    # Authoritative canonical context
│   │   ├── _meta.yaml              # Schema version, project metadata
│   │   ├── requirements.yaml        # All requirements (FR, NFR)
│   │   ├── decisions.yaml           # All decisions (ADR, escalations)
│   │   ├── specifications.yaml      # All technical specs
│   │   ├── spikes.yaml              # All spikes + findings
│   │   ├── work_items.yaml          # All work items
│   │   ├── implementation_plans.yaml # Versioned proposed/accepted implementation plans
│   │   ├── milestones.yaml          # All milestones
│   │   ├── verification.yaml        # Verification evidence
│   │   ├── risks.yaml               # Risks and blockers
│   │   ├── handoffs.yaml            # Session/developer handoffs
│   │   └── relationships.yaml       # Graph of entity relationships
│   │
│   ├── graph/                       # Optional: pre-computed graph indices
│   │   ├── depends_on.idx
│   │   ├── affects.idx
│   │   └── component_map.idx
│   │
│   └── state/
│       ├── active_work.yaml         # Current in-progress work
│       └── last_validated.yaml      # Timestamp each file was checked
```

**Rationale for file separation:**
- One file per entity kind (easier to edit, fewer merge conflicts)
- All relationships in one file (clearer graph structure)
- Metadata and state separate (clear authority boundaries)
- Indexed views optional (for performance, regenerated from authoritative files)

### Schema Version

```yaml
# .sdlc/context/_meta.yaml
project:
  name: "web-app-project"
  created_at: "2026-08-15T10:00:00Z"
  
schema:
  version: "2.0.0"                      # Semantic versioning (major: mandatory plan semantics)
  format: "yaml"                        # Canonical format
  encoding: "utf-8"
  validation_url: "https://..."         # Optional: schema URL for tooling
  
# Backward compatibility
compatibility:
  minimum_reader_version: "2.0.0"      # 1.x readers are not compatible with required plan semantics
  minimum_writer_version: "2.0.0"      # writers must preserve plan identity/revision/acceptance
  
# Profile and rigor
active_profile: "standard"              # lightweight|standard|high_rigor
rigor_overrides:                        # Project-specific deviations
  security_critical: "high_rigor"
  
# Bootstrap
bootstrap:
  agent_instructions: "AGENTS.md"       # Path to agent bootstrap
  context_ready: false                  # Is context initialized?
```

### Example: requirements.yaml

```yaml
# .sdlc/context/requirements.yaml
entities:
  - id: "FR-001"
    kind: "requirement"
    status: "accepted"
    summary: "User can sign in with email/password"
    description: |
      As a user, I want to sign in with email and password
      so that I can access my account securely.
    
    acceptance_criteria:
      - "User can enter email and password"
      - "System validates credentials against auth service"
      - "Session is created for valid credentials"
      - "Error message shown for invalid credentials"
      - "Rate limiting prevents brute-force attacks"
    
    source:
      file: "docs/requirements/authentication.md"
      line: 12
      commit: "a1b2c3d4e5f6"
    
    authority: "product_owner"
    rigor_profile: "standard"
    tags: ["authentication", "critical"]
    
    created_at: "2026-08-15T10:30:00Z"
    last_validated: "2026-08-17T14:22:00Z"
    validation_status: "current"
    
    relationships:
      - target: "ADR-003"
        type: "governed_by"
      - target: "SPIKE-001"
        type: "depends_on"
    
    depends_on: ["ADR-003", "COMP-auth"]
    affects: ["SPEC-002", "WI-042", "VER-087"]

  - id: "FR-002"
    kind: "requirement"
    status: "accepted"
    summary: "System stores passwords securely"
    description: "Passwords must be hashed with bcrypt or equivalent"
    
    source:
      file: "docs/requirements/authentication.md"
      line: 35
      commit: "a1b2c3d4e5f6"
    
    authority: "product_owner"
    created_at: "2026-08-15T11:00:00Z"
    last_validated: "2026-08-17T14:22:00Z"
    validation_status: "current"
    
    relationships:
      - target: "ADR-003"
        type: "governed_by"
      - target: "SPEC-002"
        type: "specified_by"

  - id: "NFR-001"
    kind: "nfr"
    status: "proposed"
    summary: "Sign-in latency must be <200ms (p95)"
    description: "User experience requires fast authentication"
    
    source:
      file: "docs/requirements/performance.md"
      line: 8
      commit: "a1b2c3d4e5f6"
    
    authority: "architect"
    created_at: "2026-08-16T09:00:00Z"
    last_validated: "2026-08-16T09:00:00Z"
    validation_status: "stale"  # Not yet approved by product
    
    relationships: []
    depends_on: []
    affects: ["SPEC-002"]
```

### Example: decisions.yaml

```yaml
# .sdlc/context/decisions.yaml
entities:
  - id: "ADR-003"
    kind: "decision"
    status: "accepted"
    summary: "Use bcrypt for password hashing"
    description: |
      We will use bcrypt for password hashing instead of:
      - Plaintext (insecure)
      - MD5 (weak hash)
      - Argon2 (overkill for our scale)
      
      Trade-offs: bcrypt is slower than MD5 (good for security),
      but adds ~100ms to auth path (acceptable given NFR-001 budget).
    
    decision_type: "architecture"
    options_considered:
      - name: "Plaintext"
        risk: "High security risk"
      - name: "MD5"
        risk: "Cryptographically weak"
      - name: "Argon2"
        risk: "Performance overhead at scale"
      - name: "bcrypt (chosen)"
        rationale: "Good security/performance balance"
    
    source:
      file: "docs/adr/ADR-003.md"
      line: 1
      commit: "b2c3d4e5f6a7"
    
    authority: "architect"
    created_at: "2026-08-15T15:00:00Z"
    last_validated: "2026-08-17T14:22:00Z"
    validation_status: "current"
    
    relationships:
      - target: "FR-001"
        type: "governs"
      - target: "SPEC-002"
        type: "constrains"

  - id: "ESC-015"
    kind: "decision_escalation"
    status: "blocked"
    summary: "Decision required: Session revocation granularity"
    description: |
      Currently unresolved: Should users be able to revoke individual sessions
      or only sign out globally?
      
      Options:
      - Option A: Individual session revocation (more secure, more complex)
      - Option B: Global sign-out only (simpler, less flexible)
      
      Impact: Affects WI-042 (session management implementation)
    
    blocking_work_items:
      - "WI-042"
      - "WI-043"
    
    authority_required: "product_owner"
    created_at: "2026-08-17T10:15:00Z"
    created_by: "ai_agent_claude_haiku"
    
    relationships:
      - target: "WI-042"
        type: "blocks"
    
    depends_on: []
    affects: ["WI-042", "WI-043", "SPEC-002"]
```

### Example: relationships.yaml

```yaml
# .sdlc/context/relationships.yaml
# Canonical graph of all entity relationships
relationships:
  - from: "FR-001"
    type: "governed_by"
    to: "ADR-003"
    created_at: "2026-08-15T10:30:00Z"
    
  - from: "FR-002"
    type: "specified_by"
    to: "SPEC-002"
    created_at: "2026-08-15T11:00:00Z"
    
  - from: "WI-042"
    type: "implements"
    to: "FR-001"
    created_at: "2026-08-16T12:00:00Z"
    
  - from: "WI-042"
    type: "depends_on"
    to: "SPIKE-001"
    created_at: "2026-08-16T12:00:00Z"

  - from: "PLAN-WI-042"
    type: "plans"
    to: "WI-042"
    created_at: "2026-08-16T13:00:00Z"

  - from: "PLAN-WI-042"
    type: "depends_on"
    to: "SPEC-002"
    created_at: "2026-08-16T13:00:00Z"
    
  - from: "ADR-005"
    type: "supersedes"
    to: "ADR-002"
    created_at: "2026-08-17T09:00:00Z"
    
  - from: "ESC-015"
    type: "blocks"
    to: "WI-042"
    created_at: "2026-08-17T10:15:00Z"

# Derived indices (optional, regenerated)
# depends_on graph (what depends on what)
dependency_graph:
  "WI-042": ["SPIKE-001", "ADR-003"]
  "PLAN-WI-042": ["WI-042", "SPEC-002", "ADR-003"]
  "SPEC-002": ["ADR-003", "FR-001", "FR-002"]
  
# Affects graph (if this changes, what becomes stale)
affects_graph:
  "ADR-003":
    - "FR-001"
    - "FR-002"
    - "SPEC-002"
    - "WI-042"
  "FR-001":
    - "SPEC-002"
    - "WI-042"
  "WI-042":
    - "PLAN-WI-042"
  "SPEC-002":
    - "PLAN-WI-042"
```

---

## 4. Staleness & Invalidation Metadata

### Staleness Model

```yaml
# Within each entity:
validation_status:
  state: "current"                    # current|stale|needs_recheck|conflicted
  last_validated: "2026-08-17T14:22:00Z"
  validated_against:
    source_file: "docs/requirements.md"
    source_commit: "abc123def456"
  invalidated_by:                     # What change made this stale?
    - entity: "ADR-003"               # This entity was updated
      change: "decision"
      when: "2026-08-18T09:00:00Z"
      
# Dependencies (for cascade detection)
depends_on:                           # If any of these change, revalidate
  - "ADR-003"
  - "COMP-auth"
  
affects:                              # If this changes, these become stale
  - "SPEC-002"
  - "WI-042"
  - "VER-087"
```

### Staleness Propagation Example

```text
Change: ADR-003 updated (session model revised)
  ↓
Marks ADR-003 validation_status = "current" (just revalidated)
  ↓
Finds all entities with depends_on: ["ADR-003"]
  ↓
  FR-001 (depends_on ADR-003) → validation_status = "stale"
  FR-002 (depends_on ADR-003) → validation_status = "stale"
  SPEC-002 (depends_on ADR-003) → validation_status = "stale"
  WI-042 (depends_on ADR-003) → validation_status = "stale"
  PLAN-WI-042 (depends_on ADR-003/SPEC-002/WI-042) → validation_status = "stale"
  ↓
Finds downstream entities
  ↓
  VER-087 (depends_on SPEC-002/WI-042) → validation_status = "stale"
```

---

## 5. Interoperability (Read-Only Views)

### JSON Export (Optional)

```json
// Optional: .sdlc/export/context.json (regenerated from YAML)
// This is read-only for API/tooling use, not authoritative
{
  "project": "web-app-project",
  "schema_version": "2.0.0",
  "export_date": "2026-08-17T15:00:00Z",
  "entities": [
    {
      "id": "FR-001",
      "kind": "requirement",
      "status": "accepted",
      "summary": "User can sign in with email/password",
      ...
    }
  ],
  "relationships": [
    {
      "from": "FR-001",
      "type": "governed_by",
      "to": "ADR-003"
    }
  ]
}
```

**How to maintain consistency:**
- YAML is authoritative (edited by agents/humans)
- JSON is generated by `sdlc-setup` or CI after each YAML edit
- Tools read JSON; never write JSON directly
- JSON schema validates against canonical YAML structure
- If JSON edit attempted: error "context.json is read-only; edit .sdlc/context/*.yaml"

---

## 6. Schema Versioning & Migration

### Versioning Strategy: Semantic Versioning

```
Schema version: MAJOR.MINOR.PATCH

1.0.0 → 1.0.1: Backward-compatible (new optional fields)
1.0.0 → 1.1.0: Backward-compatible (new optional entity kinds/relationships)
1.0.0 → 2.0.0: Breaking change for readers — required new entity/relationship
               semantics, mandatory fields, or raised minimum_reader that makes
               1.x readers unable to interpret the document correctly
```

This repository treats the introduction of mandatory `implementation_plan` /
`accepted_plan` (with acceptance evidence) semantics as a **major** bump to
`2.0.0`. Calling that change a SemVer minor while also setting
`minimum_reader_version` above 1.0.0 would be misleading: a 1.0 reader is not
semantically compatible.

### Compatibility Rules

```yaml
# In _meta.yaml
compatibility:
  minimum_reader_version: "2.0.0"    # 1.x readers must not consume required plan semantics
  minimum_writer_version: "2.0.0"    # Writers must preserve plan identity/revision/acceptance
  
# Compatibility note:
# Under Semantic Versioning for this schema:
# - optional additive fields/kinds may be minor/patch;
# - making new entity kinds or fields mandatory for correct interpretation is MAJOR;
# - unknown required entity kinds must never be silently ignored;
# - major-version changes require migration.
```

### Migration Path (v1.0.0 → v2.0.0)

This is the migration for the breaking change that caused the 2.0.0 bump: mandatory implementation-plan identity and acceptance evidence. It is not a rename of unrelated decision fields.

```yaml
# docs/migrations/v1-to-v2.yaml
version_from: "1.0.0"
version_to: "2.0.0"

changes:
  - entity: "implementation_plan"
    change_type: "new_required_semantics"
    description: "Durable proposed plan revisions. 1.x projects do not have them."

  - field: "accepted_plan"
    entity: "work_item"
    change_type: "new_required_before_implementation"
    description: "Pointer to plan_id + plan_revision plus accepted_by and accepted_at. Must not be fabricated from an old plan file or from agent output."

  - field: "candidate_lifecycle_stage"
    entity: "merge_candidate"
    change_type: "new_when_candidate_exists"
    description: "Durable IMPLEMENTATION_IN_PROGRESS or IN_REVIEW. Missing stage is reconstructed, never defaulted to IN_REVIEW."

migration_rules:
  - "Do not copy a generated or historical plan into accepted_plan."
  - "Do not invent accepted_by, accepted_at, or acceptance_source."
  - "A 1.x work item with no recorded technical-authority acceptance has no accepted plan."

migration_steps:
  - step: 1
    description: "Inventory work items that already have implementation in progress or a merge candidate."
    action: "Mark each of those work items NOT_READY for further implementation until the steps below finish."

  - step: 2
    description: "Propose a plan without accepting it."
    action: "Run implementation-planning. Persist plan_status PROPOSED. Leave accepted_plan unset."

  - step: 3
    description: "Accept only through project technical authority."
    action: "An authorized person or policy operation records accepted_by and accepted_at and then advances accepted_plan. Planning output is not this step."

  - step: 4
    description: "Re-run development-readiness."
    action: "Implementation stays blocked until readiness returns READY against the accepted revision."

  - step: 5
    description: "Record candidate stage from evidence, not from the migration itself."
    action: "If accepted scope is still incomplete, set IMPLEMENTATION_IN_PROGRESS. If scope is complete and the candidate is already in review, set IN_REVIEW. If that cannot be shown, set UNKNOWN and do not route to address-pr-review."

  - step: 6
    description: "Leave not-yet-started 1.x work without an accepted plan."
    action: "Those items gain a plan only when planning and acceptance actually happen. Absence is not backfilled."
```

Work that was implementable under 1.x does not stay implementable merely because a plan document can be generated. Affected implementation work is not-ready until a plan is proposed and explicitly accepted.

---

## 7. Acceptance Criteria for P0-02

- [ ] Logical data model defined (entity kinds, minimal fields, relationships)
- [ ] YAML serialization format specified with directory structure
- [ ] One worked example project (greenfield web app):
  - [ ] requirements.yaml with 5+ requirements
  - [ ] decisions.yaml with 2+ decisions + 1 escalation
  - [ ] relationships.yaml showing full graph
  - [ ] _meta.yaml with schema version
- [ ] Staleness metadata model (validation_status, depends_on, affects)
- [ ] Staleness cascade algorithm with example (ADR change → cascade effects)
- [ ] JSON interop spec (read-only export from YAML)
- [ ] Schema versioning strategy with migration path example
- [ ] No parallel YAML/JSON representations; YAML is authoritative
- [ ] Phase 1 teams can implement context storage based on this spec

---

## 8. Next Phase 0 Workstreams

After P0-02 (Context Data Model) is locked:

- **P0-01:** Routing & Precedence (depends on context model for decision escalation state)
- **P0-03:** Staleness & Invalidation (depends on context model structure)
- **P0-04:** Multi-Agent Consistency (depends on context schema for conflict detection)
- **P0-05:** Resumability (depends on context model for work state)
- **P0-06:** Rigor Profiles (depends on context model for artifact types)
- **P0-07:** Evaluation Standard (independent; can proceed in parallel)
- **P0-08:** Decision Escalation (depends on context model for escalation state)
- **P0-09:** Integrated Lifecycle Validation (depends on all others)

---

## Decision Log

**Decision:** YAML is canonical context format  
**Rationale:** Human-readable, git-friendly, nested structure matches entity relationships  
**Alternative:** JSON (rejected: verbose, no comments), SQLite (rejected: not portable, binary)  
**Status:** DECIDED  
**Date:** 2026-08-17

**Decision:** One file per entity kind (requirements.yaml, decisions.yaml, etc.)  
**Rationale:** Easier editing, fewer merge conflicts, clear separation of concerns  
**Status:** DECIDED  
**Date:** 2026-08-17

**Decision:** JSON export is optional and read-only  
**Rationale:** Prevents context divergence; maintains YAML as single source of truth  
**Status:** DECIDED  
**Date:** 2026-08-17
