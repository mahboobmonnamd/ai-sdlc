# AI-Native SDLC Skills Suite
## Product Requirements Document (PRD) — v0.2

**Status:** Requirements baseline / architecture-ready  
**Date:** 17 August 2026  
**Target ecosystem:** Open Agent Skills format and skills.sh distribution  
**Product type:** Open, generic, reusable SDLC skill suite for AI-assisted software development

### Revision v0.2 — Requirements hardening

This revision strengthens the baseline in eleven areas discovered during critical review:

1. explicit skill-routing contract and conflict handling;
2. artifact ownership and mutation authority;
3. decision-authority boundaries;
4. minimum context data contract;
5. durable context write policy;
6. staleness/invalidation behavior;
7. lightweight, standard, and high-rigor project profiles;
8. evaluation contract and baseline comparison;
9. explicit separation of test design, acceptance testing, and verification;
10. risk-triggered specialist-review rules; and
11. multi-agent consistency, conflict detection, and resumability.

A future SDLC orchestrator agent is intentionally retained as a later delivery option. It is **not an MVP dependency**; the portable skills remain the primary product.

---

## 1. Executive Summary

AI coding agents can generate code quickly, but the quality of the result is strongly constrained by the quality of the context, decisions, requirements, work-item definition, verification, and project continuity available to the agent. A short or vague request often causes an agent to make hidden assumptions, over-scope a change, invent architecture, skip missing decisions, or declare work complete before the intended outcome is actually proven.

This project will create a **generic AI-native SDLC skills suite** that guides developers and coding agents from a vague idea to a verified, releasable software change. The suite will be reusable across products, programming languages, frameworks, repositories, issue trackers, and compatible AI coding agents.

The project is **not** intended to be a collection of long prompts or a replacement for engineering judgment. It will provide reusable expert procedures, stage gates, orchestration, and a local project-context mechanism that helps agents progressively reduce ambiguity before increasing implementation commitment.

The core operating model is:

```text
VAGUE IDEA
    ↓
DISCOVER
    ↓
DEFINE
    ↓
DESIGN
    ↓
CHECK READINESS
    ↓
RESOLVE UNCERTAINTY
    ↓
PLAN WORK
    ↓
DEVELOP / REVIEW / VERIFY  ↺
    ↓
RELEASE
    ↓
PROVEN OUTCOME
```

Cross-cutting orchestration continuously answers:

```text
Where are we?
What is complete?
What is blocked?
What should happen next?
What changed?
What evidence proves completion?
```

---

## 2. Problem Statement

### 2.1 Current problem

Developers increasingly work through AI coding agents using brief natural-language instructions. This improves speed but introduces recurring failure modes:

1. The developer starts with a vague idea and the agent turns assumptions directly into implementation.
2. Requirements are generated without sufficient discovery, criticism, or contradiction checking.
3. Architecture decisions are invented while writing code instead of being explicitly decided.
4. Technical uncertainty is discovered late, blocking implementation after work has already started.
5. Work items omit context, scope boundaries, acceptance criteria, dependencies, or verification.
6. Agents lose project continuity between sessions and repeatedly scan large repositories.
7. Different agents or team members develop inconsistent understandings of the same project.
8. Developers do not always know the correct next SDLC activity.
9. Milestone progress is inferred from closed tickets rather than traceable acceptance outcomes.
10. Code may compile and tests may pass while the requested product behavior is still incomplete.
11. AI agents tend to be agreeable and may silently accept poor assumptions or proposed solutions.
12. Existing high-quality skills are often task-specific; developers need a coherent SDLC workflow across skills.

### 2.2 Why conventional prompts are insufficient

A prompt can tell an agent what output to produce. A reusable skill should instead define **how to perform a class of work well**, including discovery, challenge, validation, refusal to invent missing decisions, and evidence required for completion.

The project therefore treats good AI-assisted engineering as:

```text
Project Context
      +
Reusable Expert Procedure
      +
Explicit Decisions
      +
Deterministic / Evidence-Based Verification
      =
Higher-quality software outcome
```

---

## 3. Product Vision

Create an open SDLC capability layer that lets a developer begin with a short request while the agent:

- discovers missing context;
- challenges invalid assumptions;
- determines the correct SDLC activity;
- creates or improves the appropriate artifact;
- checks readiness before implementation;
- uses spikes to resolve technical uncertainty;
- designs implementation-ready work items;
- maintains traceability and project continuity;
- performs development in an iterative loop;
- verifies outcomes against requirements rather than merely code state; and
- keeps enough persistent project knowledge locally that future agents do not need to reread the entire project.

### 3.1 Product promise

> **Reduce ambiguity before increasing implementation commitment.**

### 3.2 Intended users

- Individual developers using AI coding agents
- Software architects
- Technical leads
- Product-minded engineers
- Small engineering teams
- Larger teams that want tracker-agnostic reusable SDLC procedures
- Open-source maintainers using multiple AI agents

### 3.3 Supported project classes

The skills must remain applicable to:

- Web applications
- Mobile applications
- APIs and backend services
- CLIs and developer tools
- Desktop applications
- Infrastructure / platform software
- Data systems
- Embedded or systems software
- Libraries and SDKs
- Existing brownfield systems and new greenfield projects

---

## 4. Goals

### G-001 — Generic reusability
Skills must not be tied to one application, repository, programming language, framework, cloud platform, issue tracker, or AI agent.

### G-002 — Better decisions before code
The suite must prevent vague product intent from silently becoming implementation decisions.

### G-003 — Context-efficient AI development
Agents should load relevant project context without needing to reread the full repository on every interaction.

### G-004 — Continuous SDLC navigation
The developer should be able to ask what to do next without memorizing the skill suite.

### G-005 — Readiness before implementation
Development should begin only when requirements and technical dependencies are sufficiently understood, or after the appropriate spike / decision loop.

### G-006 — Strong work-item quality
Work items must contain enough outcome, scope, acceptance, dependency, and verification information for a human or agent to execute reliably.

### G-007 — Evidence-based completion
Completion must be based on traceable acceptance criteria and verification evidence, not simply task closure or code generation.

### G-008 — Team continuity
Project context and work state should survive agent sessions and be shareable through the project repository.

### G-009 — Composability
Each skill should be useful independently while also composing into a coherent end-to-end SDLC.

### G-010 — Measurable skill quality
Every published skill must be evaluated against realistic cases and demonstrate value over an unskilled baseline.

### G-011 — Explicit authority boundaries
The suite must distinguish what an agent may infer, recommend, propose, validate, or decide, and must escalate decisions that require product, architecture, compliance, or human authority.

### G-012 — Resumable multi-agent development
Durable SDLC state must allow a later session, agent, or developer to reconstruct the current work state without relying on hidden conversation memory.

---

## 5. Non-Goals

The project will not:

- replace project managers, architects, security specialists, lawyers, compliance owners, or domain experts;
- make product decisions that require explicit user or stakeholder authority;
- assume a specific issue tracker such as GitHub Issues, Jira, Linear, GitLab, or Azure DevOps;
- require a proprietary hosted memory service;
- rely on model/account memory as the source of project truth;
- require a single coding agent vendor;
- force every project to adopt a heavyweight document set;
- turn every small change into a full enterprise SDLC;
- require every cross-cutting review for every work item;
- automatically convert technical unknowns into product decisions;
- treat generated project-context summaries as authoritative over source artifacts and code.
- require users to install or use a custom orchestrator agent for core functionality;
- define a vendor-specific agent installation mechanism as part of the MVP.

---

## 6. Foundational Principles

### P-001 — Source of truth remains authoritative
Code, approved requirements, ADRs, specifications, tests, and user-approved decisions remain authoritative. The context graph is an index/cache, not truth.

### P-002 — Separate fact, assumption, unknown, and decision
Skills must not silently convert assumptions into project facts.

Conceptually, relevant outputs should distinguish:

```text
KNOWN
ASSUMED
UNKNOWN
DECISION REQUIRED
```

### P-003 — Critical rather than agreeable
A skill must be able to reject, challenge, or escalate a user request when it is contradictory, underdefined, technically unjustified, or outside the authority of the current activity.

### P-004 — Progressive disclosure
Agents should load only the instructions and project context needed for the current task.

### P-005 — Tracker agnostic
Skills design content. The user or host agent decides where content is persisted.

### P-006 — Agent agnostic
Skills must use the open Agent Skills conventions where possible and avoid vendor-specific assumptions unless isolated in optional adapters.

### P-007 — Technology agnostic
A generic skill may inspect the technology actually present in a project, but must not prescribe one before discovery.

### P-008 — Artifact ownership
Artifact-producing skills own an artifact from discovery through validation, not merely generation.

### P-009 — Verification is separate from generation
Creating code or an artifact does not prove correctness.

### P-010 — Right-size rigor
A tiny maintenance task should not require the same ceremony as a security-sensitive distributed-system change.

### P-011 — Technical spikes reduce uncertainty
Spikes exist to answer specific technical questions with evidence; they do not become uncontrolled production implementation.

### P-012 — Traceability should be preserved
When practical, the system should maintain relationships from problem → requirement → decision → work → code/test → verification → release.

### P-013 — Decision authority is explicit
Skills may recommend decisions but must not silently claim authority they do not have. Product behavior, architecture, technical evidence, implementation approach, and verification status have different decision owners.

### P-014 — Durable memory is curated
Not every observation belongs in persistent project context. Assumptions, transient notes, and unverified conclusions must not be promoted to durable facts automatically.

### P-015 — Workflows are resumable
Meaningful SDLC state transitions must be reconstructable from durable project state so work can continue across sessions, agents, or developers.

### P-016 — Concurrent updates fail visibly
When multiple agents or humans change related project state, conflicting or stale updates must be detected and surfaced rather than silently overwriting newer information.

---

## 7. SDLC Operating Model

### 7.1 Main lifecycle

```text
Product Discovery
       ↓
Product Requirements
       ↓
Architecture Design
       ↓
Technical Specification
       ↓
Development Readiness
       │
       ├── READY ───────────────────────────┐
       │                                    │
       ├── TECHNICAL UNKNOWN                │
       │       ↓                            │
       │   Technical Spike                  │
       │       ↓                            │
       │   Evidence / Findings              │
       │       ↓                            │
       │   Update ADR / Spec                │
       │       └────→ Readiness Check ──────┤
       │                                    │
       ├── PRODUCT DECISION REQUIRED        │
       │       └────→ Product / User ───────┤
       │                                    │
       └── ARCHITECTURE DECISION REQUIRED   │
               └────→ Architecture ─────────┘
                                            ↓
                                   Development Loop
                                            │
                                   Impact Analysis
                                            ↓
                                   Work Item Design
                                            ↓
                               Implementation Planning
                                            ↓
                                      Test Design
                                            ↓
                                    Implementation
                                            ↓
                                      Code Review
                                            ↓
                                      Verification
                                  FAILED ↺       PASSED
                                                  ↓
                                        Release Readiness
                                                  ↓
                                                Done
```

### 7.2 Development is a loop

Implementation planning, test design, development, code review, and verification are not one-time project phases. They are repeated for each meaningful feature, bug, change, or work item.

### 7.3 Readiness is a routing gate

A readiness failure must be classified instead of generically blocking:

| Readiness gap | Route |
|---|---|
| Technical feasibility unknown | Technical spike |
| Product behavior unknown | Product / requirements decision |
| Architecture choice unresolved | Architecture decision |
| Acceptance criteria missing | Requirements / work-item refinement |
| Dependency unavailable | Dependency/blocker management |
| Compliance/legal question | External/domain owner |

### 7.4 SDLC routing contract

Routing is a **product requirement**, while the eventual router implementation is an architecture decision.

A routing decision shall conceptually consider:

```text
CURRENT PROJECT STATE
+
AVAILABLE / MISSING ARTIFACTS
+
UNRESOLVED CONDITIONS
+
USER'S REQUESTED OUTCOME
+
WORK RISK / RIGOR PROFILE
        ↓
ROUTING DECISION
        ↓
NEXT CAPABILITY + RATIONALE
```

The routing result must include:

- selected next capability or explicit stop condition;
- reason the capability is appropriate now;
- blocking condition, if any;
- evidence/context used for the decision;
- alternative route when ambiguity remains.

Routing precedence must prevent unsafe shortcutting. At minimum:

1. explicit unresolved product/authority decisions outrank implementation work;
2. material technical uncertainty routes to a spike before production implementation;
3. missing testable acceptance behavior routes to refinement before verification;
4. implementation cannot route directly to `DONE` without verification;
5. stale or conflicting authoritative context routes to reconciliation before relying on it.

Closely related skills must define negative boundaries so more than one skill does not claim the same request without a clear precedence rule.

The PRD does **not** require a specific state-machine, rules engine, script, or orchestrator-agent implementation.

---

## 8. Skill Taxonomy

The suite will contain three primary skill classes plus foundational support.

### 8.1 Artifact Skills

Artifact skills discover, challenge, produce, and validate an SDLC artifact.

Candidate capabilities:

- `product-discovery`
- `product-requirements`
- `architecture-design`
- `technical-specification`

### 8.2 Execution Skills

Execution skills perform or guide development activities.

Candidate capabilities:

- `development-readiness`
- `technical-spike`
- `change-impact-analysis`
- `work-item-design`
- `implementation-planning`
- `test-design`
- `implementation`
- `code-review`
- `verification`
- `release-readiness`

### 8.3 Orchestration Skills and Future Agent Layer

Orchestration capabilities operate across the lifecycle and help developers manage progress and direction. In the core product they remain portable skills/capabilities. A future custom SDLC orchestrator agent may coordinate them automatically, but that agent is an optional experience layer rather than the source of SDLC expertise.

Candidate capabilities:

- `sdlc-navigator`
- `next-work`
- `milestone-status`
- `issue-triage`
- `project-health`
- `handoff`

The architectural separation is:

```text
SKILL    = HOW a reusable SDLC activity is performed
AGENT    = WHO may own/coordinate a workflow (optional, later)
CONTEXT  = WHAT is currently true about this project
TOOL/GATE = WHAT can be proven deterministically
```

Core functionality must remain usable without the future agent layer.

### 8.4 Context Skills

Context capabilities establish persistent, auditable project knowledge.

Candidate capabilities:

- `sdlc-setup`
- `project-context`

### 8.5 Cross-Cutting Specialist Skills

These may be created, reused, adapted, or invoked only when relevant:

- security review
- privacy review
- performance analysis
- accessibility review
- dependency maintenance
- incident analysis
- documentation review
- database design
- API design
- frontend / experience design

The project must **not** duplicate an existing strong ecosystem skill simply to increase skill count.

---

## 9. Core Skill Requirements

### 9.1 `sdlc-setup`

**Purpose:** Establish the AI-readable project context layer and bootstrap instructions.

The skill shall:

- inspect repository structure and available documentation;
- identify languages, frameworks, build/test commands, conventions, major components, and existing SDLC artifacts;
- establish a local context workspace using a documented portable format;
- initialize a context index and relationship graph;
- record provenance for derived facts;
- establish lightweight agent bootstrap guidance;
- avoid copying the entire repository into context files;
- identify what cannot be inferred safely;
- initialize an explicit project rigor profile or infer a proposed profile for user confirmation;
- initialize context schema/version metadata;
- support re-running setup without destructively replacing user-maintained data;
- detect potentially conflicting existing context rather than silently replacing it.

The exact directory format is a design decision, but the requirements assume a project-local representation similar to:

```text
.sdlc/
├── context/
├── graph/
├── state/
└── index.*
```

### 9.2 `project-context`

**Purpose:** Maintain and retrieve relevant project knowledge efficiently.

The capability shall:

- return context relevant to the current task;
- distinguish authoritative source data from derived summaries;
- record provenance;
- track validation/staleness;
- invalidate or refresh affected context when source artifacts change;
- avoid full-project rescans when incremental validation is sufficient;
- support inspection by humans;
- support updates triggered by approved decisions, completed work, changed artifacts, or handoffs;
- avoid hidden dependence on proprietary model memory;
- apply the durable context write policy defined in Section 12;
- surface stale-write/conflict conditions before overwriting concurrent updates;
- expose enough metadata to determine source, status, confidence/authority, and last validation.

### 9.3 `sdlc-navigator`

**Purpose:** Determine the appropriate next SDLC activity.

It shall consider available project state and route to activities such as:

```text
No product definition          → discovery
Requirements incomplete        → product-requirements
Architecture unresolved        → architecture-design
Technical uncertainty          → technical-spike
Work not decomposed            → work-item-design
Work ready                     → next-work / planning
Implementation complete        → verification
Milestone candidate complete   → milestone-status / release-readiness
```

It must explain *why* the suggested activity is next and must follow the routing contract in Section 7.4.

The initial implementation may expose this as an explicitly invoked skill. A future SDLC orchestrator agent may call the same routing capability automatically when the user says things such as “continue the project” or “what should we do next.” The agent implementation and installation mechanism are deferred until the skill suite and routing behavior are proven.

### 9.4 `product-discovery`

**Purpose:** Convert a vague idea into an understood problem space.

It shall:

- identify user/problem/outcome;
- discover current alternatives;
- surface assumptions;
- challenge solution-first framing;
- identify evidence gaps;
- separate product need from proposed implementation;
- identify unresolved decisions;
- stop short of implementation design unless required for feasibility discussion.

### 9.5 `product-requirements`

**Purpose:** Own a PRD from incomplete input to validated artifact.

Required workflow:

```text
DISCOVER
→ CHALLENGE
→ CLARIFY
→ DEFINE SCOPE
→ DEFINE BEHAVIOR
→ DEFINE NFRs
→ DEFINE ACCEPTANCE
→ CHECK CONTRADICTIONS
→ CHECK COMPLETENESS
→ USER DECISIONS
→ FINALIZE
```

It shall not merely synthesize existing conversation. It must discuss missing material with the user when necessary.

It must:

- avoid inventing product decisions;
- identify conflicts;
- identify assumptions;
- define in/out-of-scope;
- define user journeys or system behavior as appropriate;
- define functional and non-functional requirements;
- create testable acceptance criteria;
- flag feasibility risks without taking over architecture;
- produce a completeness assessment before finalization.

### 9.6 `architecture-design`

**Purpose:** Convert accepted requirements into explicit technical decisions and boundaries.

It shall:

- inspect relevant existing architecture first;
- identify architectural drivers;
- compare reasonable alternatives;
- document trade-offs;
- separate facts from recommendations;
- capture important decisions as ADR-compatible content;
- reject requirements that are infeasible or internally contradictory and route them back;
- avoid implementation-detail micromanagement unless the decision requires it.

### 9.7 `technical-specification`

**Purpose:** Convert requirements and architecture into implementable behavior and contracts.

It shall:

- define component responsibilities and interfaces;
- define data behavior where applicable;
- define failure/error behavior;
- define compatibility and migration expectations;
- identify observable acceptance behavior;
- surface unresolved technical gaps;
- preserve traceability to requirements/decisions;
- avoid silently making new product decisions.

### 9.8 `development-readiness`

**Purpose:** Answer: “Do we know enough to responsibly start this work?”

Result must be one of:

- `READY`
- `SPIKE REQUIRED`
- `PRODUCT DECISION REQUIRED`
- `ARCHITECTURE DECISION REQUIRED`
- `DEPENDENCY BLOCKED`
- `REFINEMENT REQUIRED`

It shall assess, proportionate to work complexity:

- requirement clarity;
- testable acceptance criteria;
- architecture decisions;
- dependency understanding;
- major technical uncertainty;
- security/data implications;
- affected area identification;
- verification approach.

### 9.9 `technical-spike`

**Purpose:** Reduce technical uncertainty with bounded evidence.

Every spike must define:

- question to answer;
- why the answer matters;
- current unknown;
- experiment/research boundary;
- evidence required;
- expected output;
- decision enabled by the finding.

It must:

- minimize production implementation;
- identify disposable prototype code;
- record observations separately from conclusions;
- return a recommendation based on evidence;
- route findings back to the appropriate ADR/spec/requirement;
- not decide product policy.

### 9.10 `change-impact-analysis`

**Purpose:** Determine what an intended change can affect before implementation.

It shall consider as applicable:

- requirements;
- components/modules;
- public/internal APIs;
- stored data and migrations;
- compatibility;
- tests;
- security/privacy;
- performance;
- operations;
- documentation;
- deployment/release sequencing.

The output should focus planning rather than become a replacement architecture document.

### 9.11 `work-item-design`

**Purpose:** Produce implementation-ready, tracker-agnostic work-item content.

The skill shall never assume the destination system. The user or host agent may later persist the output to GitHub Issues, Jira, Linear, Azure DevOps, GitLab, a repository file, or another system.

A normal work item should contain, when applicable:

- title;
- type;
- outcome;
- context / why;
- scope;
- out of scope;
- expected behavior;
- acceptance criteria;
- decided technical constraints;
- dependencies;
- risks / unknowns;
- verification;
- artifacts/docs to update.

Ticket detail must be proportional to complexity.

#### Feature work item
Should emphasize problem context, outcome, behavior, scope, acceptance, dependencies, and verification.

#### Bug work item
Should emphasize observed vs expected behavior, reproduction, environment, impact, evidence, regression status, acceptance, and verification.

#### Technical spike
Should emphasize the precise question, evidence required, research/experiment boundary, and decision that follows.

#### Technical debt
Should emphasize current problem, impact, desired end state, why now, constraints, regression protection, and acceptance criteria.

The skill must not confuse **ticket design** with **implementation planning**.

### 9.12 `implementation-planning`

**Purpose:** Determine how a ready work item should be changed in the actual codebase.

It shall:

- load the ticket/spec/ADR/acceptance context;
- inspect the affected source area;
- identify concrete components/files where useful;
- define an implementation sequence;
- identify tests and migration steps;
- preserve scope boundaries;
- detect new uncertainty and route back to readiness/spike rather than guessing.

### 9.13 `test-design`

**Purpose:** Derive appropriate test coverage from requirements and risks.

The suite must distinguish these concepts:

```text
UNIT / COMPONENT TESTS
→ implementation correctness at a local boundary

INTEGRATION / SYSTEM TESTS
→ interaction correctness across boundaries

ACCEPTANCE TESTS / CHECKS
→ observable requirement behavior

VERIFICATION
→ evidence-based judgment that the intended work/product outcome is satisfied
```

Passing tests contributes evidence but does not automatically equal successful verification.

It shall:

- trace tests to behavior and acceptance criteria;
- choose suitable levels (unit/integration/E2E/etc.) based on the work;
- identify edge/failure cases;
- avoid implementation-coupled tests when behavior-level testing is more appropriate;
- identify gaps that make requirements untestable.

### 9.14 `implementation`

**Purpose:** Execute a ready plan safely.

It shall:

- stay within approved scope;
- respect existing architecture/conventions;
- follow project tests/build requirements;
- surface scope changes rather than silently expand work;
- update implementation evidence;
- not declare the work complete before verification.

The suite may choose to reuse existing strong implementation/TDD skills rather than create a redundant generic skill.

### 9.15 `code-review`

**Purpose:** Critically inspect implementation quality and conformance.

It shall assess applicable concerns:

- correctness;
- requirements conformance;
- maintainability;
- security;
- concurrency/data correctness;
- error handling;
- compatibility;
- tests;
- unnecessary scope;
- divergence from architecture/spec.

Review should prioritize actionable findings and avoid stylistic noise when project conventions already decide style.

### 9.16 `verification`

**Purpose:** Prove that the requested outcome is actually satisfied.

Verification must distinguish:

```text
CODE EXISTS
≠
LOCAL TESTS PASS
≠
ACCEPTANCE BEHAVIOR PASSES
≠
PRODUCT / WORK-ITEM OUTCOME VERIFIED
```

These are not equivalent.

It shall:

- trace verification to acceptance criteria;
- execute or inspect relevant evidence;
- identify unverified criteria;
- reject “done” when evidence is incomplete;
- validate relevant docs/migrations/operational behavior when applicable;
- update completion state only after successful verification.

### 9.17 `release-readiness`

**Purpose:** Determine whether a verified change is safe and prepared for release.

It shall consider, as applicable:

- configuration;
- migrations;
- deployment order;
- rollback;
- feature flags;
- backward compatibility;
- secrets;
- observability;
- operational documentation;
- known risks;
- release verification.

### 9.18 `issue-triage`

**Purpose:** Turn incoming reports into correctly understood actionable outcomes.

It shall:

- classify bug/feature/question/regression/tech debt/spike candidate;
- separate reported problem from proposed solution;
- assess impact/severity proportionately;
- identify duplicates where available;
- identify affected requirements/components where possible;
- determine readiness or missing information;
- route unresolved product or technical questions appropriately.

### 9.19 `next-work`

**Purpose:** Recommend the highest-value ready work rather than the next arbitrary TODO.

It shall consider:

- milestone priority;
- dependencies;
- blockers;
- readiness;
- risk;
- incomplete acceptance criteria;
- available spikes/decisions.

The recommendation must state why the item is ready and why higher-priority alternatives are not selected.

### 9.20 `milestone-status`

**Purpose:** Determine actual milestone completion.

It must not equate completion with the percentage of closed tickets.

Completion should be derived from:

- milestone outcomes;
- requirements;
- acceptance criteria;
- verified work;
- unresolved blockers/risks.

### 9.21 `project-health`

**Purpose:** Audit whether SDLC execution is becoming inconsistent or unsafe.

Potential findings include:

- implementation ahead of requirements/spec;
- requirements without acceptance criteria;
- ADR changed but dependent specs remain stale;
- milestone acceptance blocked by defects;
- tests not traceable to expected behavior;
- spike findings not incorporated into decisions;
- “complete” work without verification;
- context graph staleness;
- unresolved critical decisions;
- excessive work-in-progress or blocked work if such state is available.

### 9.22 `handoff`

**Purpose:** Preserve active-work continuity across agent sessions or developers.

It should record:

- objective;
- completed work;
- current state;
- decisions made;
- files/components affected;
- tests/evidence;
- known failures;
- remaining work;
- open questions;
- risks;
- recommended next action.

It should update durable project context where appropriate rather than creating another isolated summary.

### 9.23 Artifact ownership and mutation authority

Skills must have explicit boundaries for artifacts they may **author, propose, validate, update, or supersede**.

Default authority model:

| Artifact / decision | Primary capability | Other skills may |
|---|---|---|
| Product problem / behavior | Product discovery / requirements | identify gaps, propose changes, request decision |
| PRD / acceptance intent | Product requirements | reference, validate consistency, propose amendments |
| Architecture / ADR | Architecture design | identify conflicts, propose changes, never silently rewrite accepted decisions |
| Technical specification | Technical specification | reference, detect drift, propose updates |
| Spike findings | Technical spike | consume evidence, challenge interpretation |
| Work item | Work-item design | refine with explicit scope/decision changes |
| Implementation plan | Implementation planning | review and adapt within accepted scope |
| Code | Implementation | review, verify, or propose changes |
| Verification status | Verification | provide evidence, but no other skill may mark verified without satisfying the verification contract |
| Milestone closure | Milestone status / governing workflow | recommend closure based on verified outcomes |

When a downstream activity discovers an upstream artifact is wrong, the default behavior is:

```text
DISCOVER CONFLICT
      ↓
RECORD EVIDENCE / FINDING
      ↓
PROPOSE UPSTREAM CHANGE
      ↓
ROUTE TO CAPABILITY / AUTHORITY THAT OWNS IT
      ↓
UPDATE DEPENDENTS AFTER ACCEPTANCE
```

Direct mutation is allowed only where the project policy explicitly grants that authority.

### 9.24 Decision-authority model

The suite must distinguish at least these decision classes:

| Decision class | Default authority |
|---|---|
| Product behavior / scope | User, product owner, or explicitly delegated product process |
| Architecture | Architecture process / authorized technical owner |
| Technical fact / feasibility | Evidence from spike, source, tools, tests, or documentation |
| Implementation approach | Development process within accepted requirements/architecture |
| Compliance / legal policy | Appropriate external/domain authority |
| Verification result | Verification evidence against agreed acceptance criteria |

A skill may recommend outside its authority but must label the recommendation and obtain or route to the required decision owner before persisting it as accepted fact.

---

## 10. Work-Item Quality Standard

The suite shall define a reusable work-item quality standard independent of any issue tracker.

A work item is considered ready for implementation only if a different competent developer or agent can answer:

1. Why does this work exist?
2. What outcome is required?
3. What is explicitly in scope?
4. What is explicitly out of scope when ambiguity is likely?
5. What behavior must be observable?
6. What acceptance criteria prove completion?
7. What already-decided constraints apply?
8. What dependencies or blockers exist?
9. What is still unknown?
10. How will completion be verified?

A work item must not embed speculative implementation details as requirements.

---

## 11. Definition of Ready and Definition of Done

### 11.1 Definition of Ready (DoR)

DoR is a policy used by `development-readiness`, not necessarily a separate user-facing skill.

A work item can be `READY` when, proportionate to its complexity:

- expected outcome is understood;
- scope is sufficiently bounded;
- acceptance criteria are testable;
- relevant product decisions are resolved;
- necessary architecture decisions are resolved;
- important technical uncertainty is resolved or consciously accepted;
- required dependencies are available;
- a verification method exists.

### 11.2 Definition of Done (DoD)

DoD is enforced primarily by `verification`.

“Done” should require applicable evidence that:

- acceptance criteria are satisfied;
- required tests pass;
- regression protection is adequate;
- review findings are resolved or accepted;
- migrations/configuration are validated;
- required documentation is updated;
- operational impact is addressed;
- context/work-item state is updated;
- no critical unresolved requirement remains.

---

## 12. Persistent Project Context and Memory

### 12.1 Requirement

The system shall maintain **project-local, auditable institutional memory** so the AI does not need to rediscover the entire project for each task.

### 12.2 Memory must not mean model memory

The project shall not rely on:

- hidden chat history;
- one vendor's account memory;
- unstated agent recollection;
- opaque embeddings as the sole source of a decision.

### 12.3 Context graph

The context system should support relationships such as:

```text
Requirement FR-012
    ↓ governed-by
ADR-003
    ↓ implemented-by
Work Item WI-028
    ↓ verified-by
Verification V-044
```

and:

```text
Milestone M2
 ├── WI-021  verified
 ├── WI-022  verified
 ├── WI-023  in-progress
 └── WI-024  blocked
        ↓
      Spike S-006
        ↓
      unresolved
```

### 12.4 Provenance

Every important derived fact should record enough provenance to answer:

- Where did this fact come from?
- Is the source authoritative?
- When was it last validated?
- What artifact/version/commit supports it?

### 12.5 Staleness

The system shall assume cached context can become stale.

When relevant source material changes, the system should:

1. identify affected context;
2. invalidate or mark it stale;
3. refresh only what is needed when possible;
4. preserve conflicting historical decisions when useful;
5. never silently overwrite authoritative user-maintained artifacts.

### 12.6 Human readability

Project context must be inspectable and understandable by humans without proprietary tooling.

### 12.7 Team portability

When committed to the repository, the same durable context should be usable by multiple developers and compatible agents.

### 12.8 Minimum context data contract

The PRD does not prescribe YAML, JSON, SQLite, Markdown, or another storage representation. Whatever representation is selected later must support, at minimum:

- stable entity identifier where an entity needs relationships;
- entity type;
- human-readable summary/value;
- status (for example proposed/accepted/stale/superseded/verified where applicable);
- source/provenance reference;
- authority level or source class;
- last validation/version information;
- relationships/dependencies where applicable;
- schema version.

Illustrative logical record only:

```text
id: ADR-004
kind: decision
status: accepted
summary: <decision>
source: docs/adr/ADR-004...
validated_against: <version/commit/artifact>
relationships: [...]
```

This example is **not** a mandated serialization format.

### 12.9 Durable context write policy

The system must classify information before persisting it.

| Information | Default durable behavior |
|---|---|
| Accepted user/product decision | Persist with provenance |
| Accepted architecture decision | Persist with provenance |
| Verified technical fact / spike evidence | Persist with source/evidence |
| Verified milestone/work state | Persist/update |
| Agent assumption | Do not persist as fact |
| Unconfirmed interpretation | Keep transient or mark explicitly proposed/unknown |
| Temporary implementation note | Keep in active handoff/work state unless promoted intentionally |
| Secret/credential | Never persist in SDLC context |

Derived summaries may be regenerated; accepted decisions and source links must remain distinguishable from generated summaries.

### 12.10 Staleness and invalidation contract

The context layer must support dependency-aware invalidation without requiring a specific algorithm.

Minimum behavior:

1. when an authoritative source changes, direct derived facts from that source become stale until revalidated;
2. dependent artifacts/context must be discoverable for impact assessment;
3. changes to accepted architecture must cause dependent specifications/plans/context to be checked rather than assumed valid;
4. changes to requirements must cause affected acceptance criteria, work items, tests, and milestone status to be reconsidered;
5. context must never silently remain “verified” when its supporting evidence/version no longer matches;
6. a stale item may remain readable for history but must not be presented as current truth without a warning.

The eventual architecture may use hashes, timestamps, dependency graphs, repository commits, or another mechanism.

### 12.11 Multi-agent consistency and reconciliation

When multiple sessions, agents, or humans update related state, the system must:

- retain provenance of each update;
- detect stale writes where feasible;
- surface conflicting accepted facts/decisions;
- avoid last-writer-wins behavior for authoritative conflicts;
- support reconciliation by the appropriate artifact/decision owner;
- preserve enough history to understand what changed and why.

### 12.12 Resumability

A later session must be able to determine, from durable state and authoritative sources:

- active objective/work item;
- last completed lifecycle step;
- current readiness/review/verification state;
- unresolved blockers/decisions;
- evidence produced so far;
- recommended next action when recorded.

A handoff improves this experience, but correctness must not depend solely on a manually generated handoff document.

---

## 13. Agent Bootstrap Guidance

`sdlc-setup` should establish a minimal agent instruction, using a portable convention such as `AGENTS.md` when appropriate.

The bootstrap should be short and conceptually instruct agents to:

1. read the SDLC context index before significant SDLC work;
2. load only context relevant to the current task;
3. treat source artifacts/code as authoritative over derived context;
4. detect stale context before relying on it;
5. update durable state after meaningful approved decisions or completed work;
6. never turn assumptions into project facts silently.

The full SDLC methodology must remain in skills rather than being duplicated into project agent instructions.

### 13.1 Future SDLC orchestrator agent

The project should remain **agent-ready but not agent-dependent**.

A future custom orchestrator agent may provide a higher-level experience such as:

```text
User: "Continue this project."
        ↓
Load project context
        ↓
Evaluate routing contract
        ↓
Select appropriate SDLC skill
        ↓
Run / delegate skill
        ↓
Update durable state
        ↓
Stop for authority decision or continue to next safe step
```

Expected future responsibilities may include:

- owning workflow coordination rather than SDLC expertise;
- selecting and invoking reusable skills;
- controlling tool availability by phase where supported;
- delegating review/verification to independent subagents where useful;
- respecting readiness and verification gates;
- stopping when human/product/domain authority is required.

**MVP constraint:** no user must install a custom agent to use the skill suite. Vendor-specific agent files, installation paths, extensions, and distribution mechanisms are deferred to a later compatibility/integration phase after the portable skills demonstrate value.

---

## 14. Traceability Model

Traceability is a core platform behavior, even if it is not exposed as a standalone skill.

The target relationship chain is:

```text
Problem
  ↓
Requirement
  ↓
Architecture Decision
  ↓
Technical Specification
  ↓
Work Item
  ↓
Implementation Change
  ↓
Test / Evidence
  ↓
Verification
  ↓
Release
```

The system should be capable of answering, where data exists:

- Why does this implementation exist?
- Which requirement does this ticket satisfy?
- Which work remains for this milestone?
- Which acceptance criterion is still unverified?
- Which spec depends on a changed ADR?
- Which tests/evidence prove requirement FR-X?
- What is blocking milestone M-Y?

Traceability should degrade gracefully when a lightweight project does not maintain every artifact type.

---

## 15. Context-Aware Skill Loading

Each skill should load only relevant context.

Examples:

### Product requirements
Load:
- product definition;
- existing requirements;
- glossary;
- relevant decisions;
- known users/constraints.

### Code review
Load:
- work item;
- acceptance criteria;
- relevant specification;
- relevant ADRs;
- changed components;
- coding conventions.

### Next work
Load:
- active milestone;
- dependency graph;
- blockers;
- readiness state;
- verification status.

This requirement is intended to reduce token waste and stale-context errors.

---

## 16. Integration and Tracker Independence

### 16.1 Core behavior

The core skill must produce structured content without requiring an external service.

Example:

```text
work-item-design
       ↓
Structured Work Item
       │
       ├── GitHub Issue
       ├── Jira
       ├── Linear
       ├── GitLab
       ├── Azure DevOps
       └── Local Markdown
```

### 16.2 Persistence is delegated

If the host agent has access to the user's chosen system, it may create/update the issue after user intent is clear. The skill itself must not hardcode a tracker.

### 16.3 Optional adapters

Future adapters may add tracker-specific formatting or field mapping without changing the generic skill contract.

A tracker integration is **not required for Phase 1**. Phase 1 must prove that generic work-item content is complete and portable using a local/structured representation. Tracker proofs-of-concept belong to later integration testing so the core work-item model is not accidentally shaped around one vendor's issue schema.

---

## 17. Cross-Cutting Review Invocation

Security, privacy, performance, accessibility, and similar review should be **risk-triggered**, not globally mandatory.

Examples:

- authentication change → security review likely required;
- PII storage → privacy/security review;
- public UI → accessibility review;
- hot data path → performance review;
- schema migration → data/migration review.

The core skills should identify when specialist review is appropriate but should avoid duplicating full specialist expertise inside every skill.

### 17.1 Minimum risk-trigger model

The suite must provide a generic trigger matrix. Initial categories should include at least:

| Change signal | Specialist review normally considered |
|---|---|
| Authentication, authorization, secrets, cryptography, trust boundary | Security |
| Collection/storage/sharing of personal or sensitive data | Privacy + Security |
| Public/user-facing interactive UI | Accessibility; UX where relevant |
| Latency/throughput-sensitive path, resource-intensive processing | Performance |
| Database/schema/data migration or destructive data behavior | Data/migration review |
| Public API/protocol/serialization compatibility change | API/compatibility review |
| Dependency with elevated privilege/supply-chain impact | Security/dependency review |
| Financial, safety-critical, regulated, or legally constrained behavior | Appropriate domain/compliance owner |

This matrix is a routing aid, not proof that the review passed. Projects may add stricter triggers through configuration/context.

---

## 18. Genericity Requirements and Rigor Profiles

### NFR-GEN-001
No core skill may require a specific programming language.

### NFR-GEN-002
No core skill may require a specific framework.

### NFR-GEN-003
No core skill may require a specific source-control hosting service.

### NFR-GEN-004
No core skill may require a specific issue tracker.

### NFR-GEN-005
No core skill may depend on one AI vendor's proprietary memory feature.

### NFR-GEN-006
Agent/vendor-specific instructions must be optional adapters or compatibility notes.

### NFR-GEN-007
Skills may inspect existing project-specific choices and adapt to them.

### 18.1 Project rigor profiles

The suite must right-size process requirements without changing the underlying quality principles.

#### Lightweight
Suitable for small OSS projects, prototypes, personal projects, and low-risk maintenance.

Expected characteristics:
- minimal artifact set;
- concise requirements/work items;
- architecture captured only when decisions materially matter;
- local structured state acceptable;
- verification still required, but proportionate.

#### Standard
Default for production software and normal team development.

Expected characteristics:
- explicit requirements/acceptance for meaningful work;
- architecture/spec artifacts where relevant;
- readiness/work-item/verification discipline;
- durable context and milestone tracking.

#### High-rigor
For regulated, security-sensitive, safety-sensitive, financially material, or otherwise high-risk work.

Expected characteristics:
- stricter traceability;
- explicit approval/authority points;
- stronger specialist review triggers;
- richer evidence retention;
- stricter release/readiness gates.

A profile changes **required evidence and ceremony**, not permission to invent missing decisions or skip verification.

Projects may customize the profile, but the active profile and overrides must be visible in project context.

---

## 19. Skill Packaging Requirements

As of 17 August 2026, the Agent Skills specification defines a skill as a directory containing at minimum `SKILL.md` with YAML frontmatter and Markdown instructions. Optional `scripts/`, `references/`, and `assets/` directories may be used for progressive disclosure.

The project shall follow the open Agent Skills specification unless an explicit compatibility reason requires otherwise.

### 19.1 Minimum skill structure

```text
skill-name/
├── SKILL.md
├── references/     # optional
├── scripts/        # optional
├── assets/         # optional
└── evals/          # project quality/evaluation data
```

### 19.2 Frontmatter

At minimum:

```yaml
---
name: product-requirements
description: ...
---
```

The name must follow the current Agent Skills naming constraints.

### 19.3 Progressive disclosure

The suite should keep `SKILL.md` focused on core decision procedure and move large supporting material into references loaded only when needed.

### 19.4 Skill descriptions

Descriptions are part of routing behavior. Each description must clearly state:

- what the skill does;
- when it should trigger;
- what closely-related task should **not** trigger it.

### 19.5 Distribution

The repository shall be publishable/discoverable through skills.sh-compatible installation flows and should support installing individual skills rather than requiring the entire suite.

---

## 20. Skill Evaluation Framework

A skill is not considered production-quality because it sounds sophisticated.

Every skill must be evaluated against realistic scenarios and compared, when feasible, with an unskilled baseline.

### 20.1 Required scenario classes

At minimum consider:

- clear input;
- vague input;
- contradictory input;
- missing context;
- bad user assumption;
- overly solution-specific request;
- small/simple project;
- large/existing project;
- existing SDLC artifacts;
- no prior artifacts;
- stale/conflicting artifacts;
- work that should be rejected or routed elsewhere.

### 20.2 Quality dimensions

Evaluate whether the skill:

- avoids hallucinating project facts;
- discovers missing information;
- challenges bad assumptions;
- avoids unnecessary questions;
- produces actionable outputs;
- does not over-engineer;
- preserves scope;
- routes uncertainty correctly;
- preserves traceability;
- knows when not to proceed;
- improves outcome versus no skill;
- triggers for the right tasks and avoids false activation.

### 20.3 Evaluation contract

Each stable skill must define an evaluation contract containing:

- target capability/behavior;
- scenario/input fixture;
- relevant project context fixture;
- expected route or required output properties;
- forbidden behaviors/failure conditions;
- scoring dimensions;
- baseline run without the skill (or with the prior stable version);
- result/evidence.

The evaluation format may be JSON/YAML/another machine-readable representation later; this PRD specifies the information, not serialization.

### 20.4 Baseline comparison

Where feasible, every skill must be compared with:

1. the same model/agent without the skill; and
2. the previous stable skill version for regression testing.

Minimum measurable dimensions should include, where relevant:

- critical missing-information detection rate;
- incorrect assumption/invention rate;
- correct routing rate;
- acceptance-criteria testability/completeness;
- scope-preservation rate;
- false “ready” / false “done” rate;
- unnecessary-question rate;
- trigger precision/recall for skill activation;
- human-rated actionability/clarity for outputs that cannot be scored deterministically.

The project should prefer objective checks and rubric-based scoring over a single subjective “looks good” score.

### 20.5 Eval artifacts

The project should maintain machine-readable evaluation cases per skill in an `evals/` area compatible with the chosen Agent Skills evaluation workflow where practical.

### 20.6 Regression discipline

A skill change that improves one case but degrades another should be visible through evaluation results before release. A stable release must not knowingly introduce a critical regression in authority boundaries, routing safety, context correctness, or verification behavior.

---

## 21. Functional Requirements Summary

| ID | Requirement |
|---|---|
| FR-001 | The suite shall support a vague idea through discovery to validated requirements. |
| FR-002 | The suite shall challenge assumptions and contradictions rather than blindly comply. |
| FR-003 | The suite shall separate product decisions, architecture decisions, technical unknowns, and implementation details. |
| FR-004 | The suite shall provide a development-readiness gate. |
| FR-005 | The suite shall route technical uncertainty into bounded spikes. |
| FR-006 | The suite shall produce tracker-agnostic implementation-ready work-item content. |
| FR-007 | The suite shall support repeated plan/test/implement/review/verify development loops. |
| FR-008 | The suite shall verify outcomes against acceptance criteria. |
| FR-009 | The suite shall determine milestone completion using verified outcomes, not ticket count alone. |
| FR-010 | The suite shall recommend the next appropriate SDLC action/work. |
| FR-011 | The suite shall support issue triage that separates problems from proposed solutions. |
| FR-012 | The suite shall support project-health auditing. |
| FR-013 | The suite shall support session/developer handoff. |
| FR-014 | The suite shall establish project-local persistent context. |
| FR-015 | Persistent context shall preserve provenance and staleness information. |
| FR-016 | The suite shall support incremental context refresh. |
| FR-017 | The suite shall maintain or infer traceability relationships where artifacts exist. |
| FR-018 | The suite shall remain tracker, language, framework, and agent agnostic. |
| FR-019 | The suite shall support individually installable/composable skills. |
| FR-020 | Every published skill shall have evaluation coverage. |
| FR-021 | Skill routing descriptions shall be evaluated for trigger quality. |
| FR-022 | The suite shall right-size process rigor to work complexity. |
| FR-023 | Core skills shall be able to invoke/recommend cross-cutting specialist review when risk warrants it. |
| FR-024 | The context system shall be human-inspectable and repository-portable. |
| FR-025 | Source artifacts shall remain authoritative over derived project context. |
| FR-026 | The suite shall define routing inputs, precedence, stop conditions, and rationale requirements without prescribing the router implementation. |
| FR-027 | Artifact-producing skills shall have explicit author/propose/validate/update/supersede boundaries. |
| FR-028 | The suite shall enforce an explicit decision-authority model and escalate decisions outside the current capability's authority. |
| FR-029 | Durable context shall follow an explicit write policy separating accepted facts from assumptions and transient observations. |
| FR-030 | Context shall support dependency-aware staleness propagation and revalidation. |
| FR-031 | The suite shall support lightweight, standard, and high-rigor process profiles. |
| FR-032 | Test design, acceptance testing/checks, and final verification shall have distinct outcome definitions. |
| FR-033 | Cross-cutting specialist reviews shall be triggered by generic risk signals and project-specific overrides. |
| FR-034 | Concurrent project-state updates shall detect/surface conflicts rather than silently overwrite authoritative information. |
| FR-035 | In-progress workflow state shall be resumable across sessions/agents without depending on hidden model memory. |
| FR-036 | Stable skills shall define an evaluation contract and be compared with an unskilled/prior-version baseline where feasible. |
| FR-037 | The core skill suite shall remain usable without installing a custom orchestrator agent. |

---

## 22. Non-Functional Requirements

### NFR-001 — Portability
The skills should operate across Agent Skills-compatible clients with minimal vendor-specific behavior.

### NFR-002 — Token efficiency
Skills and context loading should minimize repeated ingestion of irrelevant repository content.

### NFR-003 — Auditability
Important project facts, decisions, status, and trace relationships must be inspectable.

### NFR-004 — Determinism where appropriate
Where a question can be answered by tools/tests/static checks, skills should prefer evidence over model opinion.

### NFR-005 — Graceful degradation
A project with only code and a README must still gain value; absence of a full artifact hierarchy must not make the suite unusable.

### NFR-006 — Low ceremony
Simple work must remain simple.

### NFR-007 — Extensibility
New specialist skills and external-system adapters should be addable without rewriting core lifecycle skills.

### NFR-008 — Safety of context
Stale context must never silently override a newer authoritative source.

### NFR-009 — Privacy
Core functionality must be usable without uploading a full private repository to a separate memory service.

### NFR-010 — Human override
A human decision can override recommendations, but the system should record explicit exceptions when they affect future reasoning.

### NFR-011 — Explainability
Readiness, routing, status, and next-work recommendations must include rationale.

### NFR-012 — Maintainability
Skills should be moderately scoped and use progressive disclosure instead of monolithic instructions.

### NFR-013 — Concurrency safety
Durable SDLC state should expose conflicts/stale writes and avoid silent authoritative last-writer-wins behavior.

### NFR-014 — Resumability
A project should be able to reconstruct active SDLC/work state after interruption from durable context and source artifacts.

### NFR-015 — Version compatibility
Skills, persistent context schema, and optional adapters must expose enough version information to detect incompatible assumptions rather than silently misread state.

---

## 23. Skill Boundary Rules

The project shall use the following decision criteria when deciding whether to create a skill.

### Create / retain a skill when:
- it represents a coherent reusable expert procedure;
- the agent is likely to perform materially worse without it;
- the behavior composes with other skills;
- it can be evaluated independently.

### Do not create a skill when:
- the behavior is project-specific context;
- the requirement is better enforced by a compiler/test/linter/CI gate;
- an existing ecosystem skill already provides equivalent or better quality;
- the proposed skill is too broad to trigger correctly;
- the proposed skill is so narrow that it creates orchestration overhead without distinct reasoning.

### Reuse / adapt before create

For every candidate capability, classify it as:

```text
REUSE
ADAPT
CREATE
DO NOT SKILL
AGENT / ROLE
TOOL / GATE
```

---

## 24. Proposed Repository Structure

This is a candidate structure, not yet a frozen implementation requirement:

```text
ai-native-sdlc-skills/
├── README.md
├── LICENSE
├── skills/
│   ├── sdlc-setup/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── evals/
│   ├── product-requirements/
│   ├── development-readiness/
│   ├── work-item-design/
│   ├── technical-spike/
│   ├── verification/
│   └── ...
├── shared/
│   ├── principles/
│   ├── schemas/
│   └── examples/
├── evals/
│   ├── harness/
│   └── fixtures/
├── docs/
│   ├── architecture/
│   ├── skill-boundaries.md
│   ├── lifecycle.md
│   └── context-model.md
└── examples/
    ├── greenfield/
    ├── brownfield/
    └── team-workflow/
```

The repository should avoid creating hidden dependencies between individually installed skills. Shared material must be packaged or referenced in a way compatible with skill installation.

---

## 25. Proposed Project Context Model

A later architecture phase shall choose a concrete representation. The minimum conceptual entities include:

- Project
- Product problem
- Requirement
- Non-functional requirement
- Decision / ADR
- Specification
- Milestone
- Work item
- Dependency
- Blocker
- Spike
- Risk
- Component
- Interface/API
- Test
- Verification evidence
- Release
- Source reference
- Handoff
- Context fact

Minimum relationship examples:

```text
requires
depends-on
blocks
implements
governed-by
specified-by
tested-by
verified-by
belongs-to-milestone
supersedes
derived-from
affects
```

Every derived entity should support provenance and status.

---

## 26. State Model

The system should avoid one generic `done/not-done` state.

Possible work states include:

```text
DRAFT
NEEDS-DECISION
NEEDS-SPIKE
NOT-READY
READY
IN-PROGRESS
IN-REVIEW
NEEDS-CHANGES
READY-FOR-VERIFICATION
VERIFIED
RELEASE-BLOCKED
DONE
```

The final state model must remain mappable to external trackers without requiring those trackers to use identical statuses.

---

## 27. User Experience Requirements

### UX-001
A developer must be able to start with a normal-language request; knowledge of every skill name should not be required.

### UX-002
Skills should ask focused questions progressively rather than presenting a large questionnaire by default.

### UX-003
When enough context already exists, skills should avoid re-asking answered questions.

### UX-004
When a skill cannot proceed, it should state the missing decision/evidence and the correct route.

### UX-005
Outputs should be concise enough to act on but complete enough to prevent avoidable ambiguity.

### UX-006
Project status and next-work outputs should prioritize actionable information over generic summaries.

### UX-007
The system should expose uncertainty explicitly.

### UX-008
Users should be able to use a single skill without adopting the full suite.

---

## 28. Example End-to-End Greenfield Journey

```text
User: "I have an idea for a developer tool."

sdlc-navigator
  → product-discovery

product-discovery
  → problem, target user, assumptions, unresolved decisions

product-requirements
  → validated PRD with acceptance criteria

architecture-design
  → architectural drivers + ADRs

technical-specification
  → implementable contracts/behavior

development-readiness
  → SPIKE REQUIRED

technical-spike
  → evidence + recommendation

architecture/spec updated

development-readiness
  → READY

work-item-design
  → first implementation-ready work items

next-work
  → selects highest-priority ready item

change-impact-analysis
implementation-planning
test-design
implementation
code-review
verification
  → pass

milestone-status
  → milestone still incomplete, identifies next unmet outcome

... loop ...

release-readiness
  → release-ready
```

---

## 29. Example Brownfield Change Journey

```text
User: "Add per-device session revocation."

sdlc-navigator
  → inspect context

issue/work-item understanding
  → identifies unresolved product policy

product decision:
  "Users may revoke individual sessions."

change-impact-analysis
  → auth API, session store, UI, audit log, tests

development-readiness
  → technical uncertainty: current token model may not support revocation

technical-spike
  → evidence: existing token design cannot revoke without server state

architecture-design
  → session model decision

work-item-design
  → tracker-agnostic feature ticket

implementation-planning
  → codebase-specific plan

test-design
implementation
code-review
verification
```

This example demonstrates that the suite must route backward when new information invalidates an earlier assumption.

---

## 30. Example Issue Triage Behavior

Incoming report:

> "Search is slow. Replace PostgreSQL with Elasticsearch."

Expected skill reasoning:

```text
Reported problem:
Search performance is unacceptable.

Proposed solution:
Replace PostgreSQL with Elasticsearch.

Status:
Solution is NOT automatically accepted as requirement.

Next action:
Measure/profile existing search and define the performance target.
Potential route:
technical spike / performance analysis.
```

The suite must prevent proposed solutions from masquerading as confirmed requirements.

---

## 31. Milestone Completion Semantics

Milestone completion should answer:

```text
What user/system outcomes were promised?
Which acceptance criteria prove them?
Which criteria are verified?
What remains unverified?
What blockers/risks prevent closure?
```

The suite must not return “80% complete” solely because 8 of 10 tickets are closed.

If a percentage is shown, its basis must be explicit and meaningful.

---

## 32. Project Health Signals

The health capability should detect patterns such as:

- open product decisions hidden inside implementation;
- architecture drift;
- stale context;
- unverified completed work;
- missing testability;
- work items with no outcome;
- blocked milestones;
- repeated reopen/rework cycles;
- high-risk work without specialist review;
- orphaned spikes;
- specs that no longer match accepted ADRs;
- requirements with no work or verification path.

The first version should focus on high-confidence signals rather than generating noisy management metrics.

Every reported health signal should include:

- finding;
- supporting evidence/source;
- impact/risk;
- recommended next capability/action;
- confidence/severity appropriate to the signal.

Phase 3 should prioritize a small set of actionable signals such as stale accepted context, unverified “done” work, unresolved milestone blockers, artifact drift, and missing acceptance/testability before expanding into broader management analytics.

---

## 33. Security and Trust Requirements

### SEC-001
No core skill may transmit repository content to an external persistence service without explicit user choice.

### SEC-002
Context files must not encourage storing secrets, credentials, tokens, or private keys.

### SEC-003
`sdlc-setup` should identify likely secret-bearing sources and exclude them from durable summaries where possible.

### SEC-004
Skills must avoid treating untrusted issue text, comments, or repository content as higher-priority instructions than the active agent/user policy.

### SEC-005
Tool execution should be limited to what the skill requires and should respect host-agent confirmation/sandbox rules.

### SEC-006
Security-sensitive changes should be routed to an appropriate security review capability when risk triggers are present.

---

## 34. Versioning and Compatibility

The suite shall:

- version skills;
- document breaking behavior changes;
- maintain migration notes for project-context schema changes;
- avoid silently changing the meaning of persistent state;
- support projects initialized by older compatible versions where practical;
- record context-schema version locally;
- expose skill version where its behavior/artifact contract can affect persisted state;
- detect incompatible context/artifact versions before mutation;
- allow optional adapters to declare compatible generic contract/schema versions.

---

## 35. Publishing Requirements

### PUB-001
Each public skill shall have a clear name and activation description.

### PUB-002
Each skill shall include examples and boundary/edge-case guidance when they materially improve performance.

### PUB-003
Each skill shall have an associated evaluation set before being considered stable.

### PUB-004
The repository shall support skills.sh discovery/installation conventions.

### PUB-005
Users shall be able to install individual skills.

### PUB-006
The project may provide curated packs such as:
- Core SDLC
- Product & Design
- Development
- Orchestration
- Team Continuity

### PUB-007
Documentation shall clearly explain what is a skill, project context, agent instruction, tool/gate, and optional adapter.

---

## 36. Success Metrics

Initial success metrics should prioritize quality rather than install counts.

### Skill-level
- Lower assumption/hallucination rate
- Higher completeness of required output
- Better contradiction detection
- Better routing of uncertainty
- Fewer unnecessary questions
- Higher acceptance-criteria quality
- Correct refusal to proceed when critical information is missing
- Improved outcome compared with baseline agent behavior

### Workflow-level
- Reduced rework caused by missing requirements
- Reduced late discovery of technical blockers
- Higher percentage of “done” work with verification evidence
- Reduced repeated repository/context reading
- Faster session/team handoff
- Higher traceability coverage for milestone-critical work

### Ecosystem-level
- Independent installs/use of individual skills
- Cross-agent compatibility
- Community contributions and reuse
- Adoption of common work-item/readiness conventions

---

## 37. Risks

### RISK-001 — Too many skills
A large fragmented suite may cause activation conflicts and cognitive overhead.

**Mitigation:** require strong skill-boundary justification and evals.

### RISK-002 — Mega-skills
Overly broad skills may load too much context and produce vague behavior.

**Mitigation:** moderate coherent scope and progressive disclosure.

### RISK-003 — Context becomes stale
Persistent memory can be more harmful than no memory if incorrect.

**Mitigation:** provenance, source authority, invalidation, incremental validation.

### RISK-004 — Process becomes heavyweight
Developers may reject the suite if every task feels bureaucratic.

**Mitigation:** right-size rigor based on complexity/risk.

### RISK-005 — Duplicate ecosystem capabilities
Creating generic TDD/review/frontend skills may add no value.

**Mitigation:** reuse/adapt/create analysis before implementation.

### RISK-006 — Agent incompatibility
Different agents implement Agent Skills/tooling differently.

**Mitigation:** open-format core with optional compatibility adapters.

### RISK-007 — False confidence from LLM review
An AI review can miss defects.

**Mitigation:** prefer deterministic evidence and explicit verification gates.

### RISK-008 — Graph complexity
A rich graph can become a product of its own.

**Mitigation:** start with minimal useful entities/relations; prove value before expansion.

---

## 38. Open Design Decisions

The following are intentionally **not decided by this PRD** and should be resolved during architecture/discovery:

1. Exact project-local context directory and file formats.
2. Whether the graph is Markdown/YAML/JSON/SQLite or a hybrid.
3. How source changes invalidate derived context.
4. Whether skill orchestration is purely instructional or assisted by scripts.
5. How to package shared references without breaking independent skill installation.
6. Whether `product-discovery` and `product-requirements` remain separate skills after evaluation.
7. Whether `implementation` is created or delegated to existing TDD/coding skills.
8. Whether `project-context` is a user-facing skill or a shared capability used by other skills.
9. How external tracker adapters map generic work-item fields.
10. Minimum traceability required for lightweight projects.
11. Skill pack composition.
12. Licensing.
13. Repository/project name and branding.
14. Context schema versioning strategy.
15. Cross-agent compatibility test matrix.
16. Whether/when to ship a custom SDLC orchestrator agent after the skills and routing contract are proven.
17. Vendor-specific agent packaging/install adapters (VS Code, Claude, other clients) if/when the agent phase is approved.

---

## 39. Recommended Delivery Phases

### Phase 0 — Ecosystem discovery and skill boundary validation
Before implementing skills:

- survey existing high-quality skills;
- classify candidates as REUSE / ADAPT / CREATE / DO NOT SKILL;
- define skill-boundary rules;
- define evaluation method;
- create representative benchmark scenarios;
- define routing and skill-boundary contract;
- define artifact/decision authority matrix;
- define minimum context/write/invalidation contracts;
- define rigor-profile semantics and risk-trigger matrix.

**Exit:** agreed capability map and no obvious duplicate/unnecessary skills.

### Phase 1 — Foundational vertical slice
Build the minimum workflow that demonstrates the thesis:

- `sdlc-setup`
- `product-requirements`
- `development-readiness`
- `technical-spike`
- `work-item-design`
- `verification`
- minimal project context/provenance
- eval harness
- lightweight + standard profile support
- explicit routing/authority/context contracts

**Exit:** vague idea → validated PRD → readiness/spike → ready work item → verification can be demonstrated generically without requiring a tracker integration or custom orchestrator agent.

### Phase 2 — Development loop
Add:

- `change-impact-analysis`
- `implementation-planning`
- `test-design` or existing skill integration
- `code-review` or existing skill integration
- release-readiness
- richer traceability

### Phase 3 — Orchestration
Add/prove:

- `sdlc-navigator`
- `next-work`
- `milestone-status`
- `issue-triage`
- `project-health`
- `handoff`
- routing behavior across the full lifecycle

After these capabilities are proven, evaluate whether a custom SDLC orchestrator agent materially improves usability. Do not build it merely because a client supports custom agents.

### Phase 4 — Ecosystem and team integrations
Add optional:

- tracker adapters;
- CI/tool integrations;
- cross-agent compatibility validation;
- skill packs;
- team workflow examples;
- specialist-skill integrations;
- optional custom SDLC orchestrator agent and vendor-specific installation adapters, only if Phase 3 evaluation justifies them.

---

## 40. Phase 1 Acceptance Criteria

Phase 1 is successful when all of the following are demonstrable:

1. A user can provide a vague software idea and `product-requirements` progressively produces a validated PRD without silently inventing critical decisions.
2. The skill flags at least representative contradictory/missing requirements in evaluation cases.
3. `development-readiness` correctly differentiates a technical spike from a product or architecture decision.
4. `technical-spike` produces a bounded evidence plan and does not treat the spike as production implementation.
5. `work-item-design` produces tracker-agnostic, appropriately sized tickets with testable acceptance criteria.
6. `verification` can reject a change that has code/tests but does not satisfy an acceptance criterion.
7. `sdlc-setup` initializes inspectable project-local context with provenance.
8. A second agent/session can load relevant project context without rereading the entire project.
9. Changing an authoritative source can mark relevant derived context stale or force revalidation.
10. Every Phase 1 skill has evals including vague, contradictory, missing-context, and bad-assumption cases.
11. Every Phase 1 skill demonstrates measurable improvement over a no-skill baseline on its target behavior.
12. The skills remain usable without GitHub/Jira/Linear and without a specific language/framework.
13. Phase 1 can run with no custom orchestrator agent installed.
14. Project context demonstrates durable-write classification: assumptions are not persisted as accepted facts.
15. A simulated authoritative artifact change causes relevant derived context to become stale/revalidation-required.
16. A representative conflicting/stale project-state update is surfaced rather than silently overwritten.
17. Lightweight profile demonstrates materially lower ceremony than standard profile while preserving acceptance and verification discipline.
18. Evaluation results include a baseline comparison for each stable Phase 1 skill.

---

## 41. Definition of Project MVP

The project MVP is **not** “all planned skills exist.”

MVP is reached when the suite proves these three claims:

### Claim A — Better requirements
A vague product request can become a more complete, critical, validated requirement artifact than default agent behavior.

### Claim B — Better development start
The system can prevent premature implementation by detecting readiness gaps and correctly routing spikes/decisions.

### Claim C — Better continuity and completion
The system can preserve enough auditable project context to continue work efficiently and can verify a work item against its acceptance outcome.

If those claims are not validated, expanding the number of skills is not justified.

---

## 42. External Ecosystem Constraints Verified for This Baseline

As of 17 August 2026:

- skills.sh describes an open agent-skills ecosystem and supports installation from repositories with `npx skills add <owner/repo>`.
- The Agent Skills specification defines a skill directory with required `SKILL.md` and optional `scripts/`, `references/`, and `assets/`.
- `SKILL.md` uses YAML frontmatter with required `name` and `description`; the specification defines naming and description constraints.
- The specification recommends progressive disclosure and keeping the main skill instructions focused.
- Agent Skills provides guidance for eval-driven skill quality assessment.
- AGENTS.md is an open convention for repository-level agent guidance and is compatible with multiple coding agents.
- Custom agents are treated as optional client-specific workflow shells; they do not replace portable skill content in this product architecture.

These are external compatibility constraints, not the product's internal architecture.

---

## 43. References

1. skills.sh — Open Agent Skills Ecosystem: https://skills.sh/
2. Agent Skills Specification: https://agentskills.io/specification
3. Agent Skills Best Practices: https://agentskills.io/skill-creation/best-practices
4. Agent Skills Evaluation Guidance: https://agentskills.io/skill-creation/evaluating-skills
5. AGENTS.md open agent instruction convention: https://agents.md/

---

## 44. Final Product Principle

The project should be judged by this question:

> **Does the suite help a developer and AI agent make fewer unjustified decisions, preserve the right context, choose the right next activity, and prove that the intended software outcome was delivered?**

If a proposed skill does not materially improve that outcome, it should not be added merely because it belongs to a conventional SDLC checklist.

Likewise, if a proposed custom agent does not materially improve orchestration beyond what the portable skills and project context already provide, it should not be built merely because an IDE supports custom agents.
