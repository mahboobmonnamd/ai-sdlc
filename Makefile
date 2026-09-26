SHELL := /bin/bash

.PHONY: test check

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

check:
	python3 -m py_compile tools/project_context.py tools/validate_skills.py tools/validate_eval_contracts.py tools/eval_judge.py tools/plan_acceptance.py tools/run_integration_eval.py tests/test_project_context.py tests/test_skill_catalog.py tests/test_eval_judge.py tests/test_plan_acceptance.py
	python3 tools/validate_skills.py
	python3 tools/validate_eval_contracts.py
	python3 tools/run_integration_eval.py --plan-only >/dev/null
	python3 tools/run_integration_eval.py --orchestration-adapter tests.eval_adapters:wiring_orchestrator >/dev/null
	python3 -m json.tool evals/core-development-loop.json >/dev/null
	python3 -m json.tool evals/integration/core-development-loop.json >/dev/null
	python3 -m json.tool evals/exclusive-work-claim.json >/dev/null
	@for f in evals/unit/*.json; do python3 -m json.tool "$$f" >/dev/null; done
	$(MAKE) test
