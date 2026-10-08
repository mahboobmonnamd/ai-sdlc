# Publishing and evaluation

AI-SDLC targets the Agent Skills format: `skills/<name>/SKILL.md`, YAML frontmatter with name/description and clear routing, context, stops, procedure, output and handoff.

Before publishing:
1. Validate skill catalog, evaluation contracts and tests with `make check`.
2. Verify all published skills have at least two unit scenarios with positive and forbidden behaviors.
3. Exercise live adapters for claim races, two implementation gates, review→processing→re-review, stale heads and merge refusal. Contract schema or wiring-fixture tests are **not** proof that skills work.
4. Check security, attribution, project-neutral support utilities, and GitHub permissions. Issue-specific workflow skills may deliberately mention GitHub because this distribution targets GitHub operations.
5. Confirm consumer migration for renamed/removed skills and publish a reviewed revision only.

No publication claim is allowed while behavioral evaluation remains `NOT_RUN`.
