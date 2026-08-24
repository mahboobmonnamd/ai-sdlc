SHELL := /bin/bash

.PHONY: test check

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

check:
	python3 -m py_compile tools/project_context.py tools/validate_skills.py tests/test_project_context.py tests/test_skill_catalog.py
	python3 tools/validate_skills.py
	python3 -m json.tool evals/core-development-loop.json >/dev/null
	$(MAKE) test
