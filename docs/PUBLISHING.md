# Publishing and validation

Agent Skills live at `skills/<name>/SKILL.md` with clear invocation, negative routing boundaries, required authority/context, stop conditions, procedure, output and handoff.

`make check` validates the catalog, tests, evaluation contracts and dashboard renderer. It does **not** prove behavior in a live repository.

Before consumer release, execute realistic tool-driven cases for claim collisions and stale claims; both implementation gates and rejected approvals; closed-unmerged candidate resume; failed/unsupported tests; single-pass complete review; review-only improvements; batched remediation; stale SHA approvals; branch protections/CI; and linked issue closure. Compare latency, human interruptions, review rounds and regressions against a baseline when available.

Do not mark behavioral evaluation `RUN` based on scripted expected-route fixtures or textual skill assertions. Publish consumer pins only after testing the target GitHub permissions and claim adapter. Historical `phase-0/` files provide provenance, not current routing instructions.
