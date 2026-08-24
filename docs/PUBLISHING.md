# skills.sh publication readiness

AI-SDLC targets the open Agent Skills ecosystem and skills.sh distribution. Publication is not a reward for having valid `SKILL.md` files; it is a release decision that requires evidence the skill set is coherent, generic, safe, and measurably useful.

## Distribution model

skills.sh installs skills directly from public GitHub repositories. After AI-SDLC is declared publish-ready, the repository install path is:

```sh
npx skills add mahboobmonnamd/ai-sdlc
```

No separate catalog-registration artifact is treated as the source of truth. The public Git repository, reviewed skill files, and release-quality evidence are authoritative for what is distributed.

## Publication gate

All mandatory items must pass before broad publication/promotion.

### 1. Catalog integrity

- Every distributed skill is under `skills/<name>/SKILL.md`.
- Frontmatter has non-empty `name` and `description`.
- Directory name and skill name match.
- Skill names are unique.
- `make check` and CI pass.
- No skill contains accidental project-specific assumptions such as Seyal architecture, product commands, or terminal-only terminology.

### 2. Routing and responsibility

Every skill defines:

- when to use it;
- when not to use it;
- required context/evidence;
- stop/escalation conditions;
- procedure;
- output/verdict contract;
- handoff/next activity.

Overlapping skills must have explicit precedence or negative boundaries. A user request must not be claimed by multiple skills with incompatible behavior.

### 3. Authority discipline

Published skills must not silently decide matters owned by product, architecture, security, privacy, legal/compliance, or another explicit authority. Unknowns must be surfaced and routed rather than converted into implementation assumptions.

### 4. Evaluation

For each published skill:

- a P0-07-compatible unit evaluation contract exists;
- representative success and failure scenarios exist;
- forbidden behaviors are explicit;
- declared passing threshold is met by the chosen evaluation harness/model set;
- results are recorded reproducibly enough to detect later regression.

At least one integration evaluation must cover the core path:

```text
development-readiness
→ work-item-design
→ implementation
→ code-review
→ verification
```

The integration test must also include a backward route when a blocking decision or stale authority is discovered.

### 5. Reference-consumer evidence

At least one real repository must consume the relevant generic capabilities without requiring them to know that project's internal architecture. Seyal is the first reference consumer, not the definition of the generic contract.

Blocking design flaws discovered through the reference consumer must be fixed in AI-SDLC before publication rather than patched only in the consumer.

### 6. Security and privacy

Review every distributed skill and tool for:

- credential/token/secret handling;
- unsafe destructive command guidance;
- accidental collection/persistence of private source or customer data;
- network/tool permissions beyond the skill's purpose;
- instructions that encourage bypassing tests, approvals, or security controls.

Context mechanisms must never treat secrets or transient reasoning as durable project facts.

### 7. Documentation and usability

The repository README must explain:

- what AI-SDLC is and is not;
- the skill/context/tool/agent distinction;
- current skill catalog;
- installation and update path;
- how projects supply their own authoritative context;
- how evaluation and publication readiness work.

Each skill description must be strong enough for compatible agents/skill discovery to choose it correctly without reading every skill first.

### 8. Public distribution decision

Before broad promotion:

- repository visibility is public;
- licensing/public-use terms are explicit and reviewed;
- release/versioning approach is decided;
- installation from a clean environment has been smoke-tested with the current skills CLI;
- published docs do not claim unimplemented skills as available.

## Current readiness

The repository is **not yet publish-ready** merely because the initial core skill files exist.

Current work must still prove:

1. core skill catalog validation and evaluation contracts pass in CI;
2. the evaluation contracts are actually executed against representative agents/models and achieve the declared threshold;
3. the Seyal reference integration is completed without blocking generic-design defects;
4. licensing/versioning/public-release decisions are explicit;
5. a clean skills.sh/skills CLI installation smoke is recorded after the merged repository contains the final publication candidate.

## Release decision

When all mandatory gates pass, create a dedicated publication Issue/PR that records the evidence and exact commit/tag being published. Publication should be reviewable and reversible; do not silently turn an in-development branch into the promoted skills.sh release.
