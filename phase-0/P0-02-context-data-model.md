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
depends_on      Entity A depends on Entity B (WI → Spike)
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
  version: "1.0.0"                      # Semantic versioning
  format: "yaml"                        # Canonical format
  encoding: "utf-8"
  validation_url: "https://..."         # Optional: schema URL for tooling
  
# Backward compatibility
compatibility:
  minimum_reader_version: "1.0.0"      # Oldest version that can read this
  minimum_writer_version: "1.0.0"      # Oldest version that can write this
  
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
  ↓
Finds all entities with depends_on: [SPEC-002, ...]
  ↓
  VER-087 (depends_on SPEC-002) → validation_status = "stale"
```

---

## 5. Interoperability (Read-Only Views)

### JSON Export (Optional)

```json
// Optional: .sdlc/export/context.json (regenerated from YAML)
// This is read-only for API/tooling use, not authoritative
{
  "project": "web-app-project",
  "schema_version": "1.0.0",
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
1.0.0 → 1.1.0: Backward-compatible (new relationship types)
1.0.0 → 2.0.0: Breaking change (entity structure changed)
```

### Compatibility Rules

```yaml
# In _meta.yaml
compatibility:
  minimum_reader_version: "1.0.0"    # Oldest reader that works
  minimum_writer_version: "1.0.0"    # Oldest writer that works
  
# Example:
# v1.0.0 can read v1.0.0-v1.2.3 (backward-compatible)
# v1.0.0 cannot read v2.0.0 (breaking change)
# v2.0.0 can read v1.x.x if migration applied
```

### Migration Path (v1.0.0 → v2.0.0 example)

```yaml
# docs/migrations/v1-to-v2.yaml
version_from: "1.0.0"
version_to: "2.0.0"

changes:
  - entity: "decision_escalation"
    change_type: "new_entity"
    description: "New entity kind for tracking unresolved decisions"
    
  - field: "decision_type"
    entity: "decision"
    change_type: "added"
    default: "architecture"
    
  - field: "old_field_name"
    entity: "requirement"
    change_type: "renamed"
    new_field_name: "new_field_name"

migration_steps:
  - step: 1
    description: "Add decision_type field with default value"
    command: "migration --step=1 --from=1.0.0 --to=2.0.0"
    
  - step: 2
    description: "Validate no breaking changes detected"
    validation: "all-entities-valid"
```

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
