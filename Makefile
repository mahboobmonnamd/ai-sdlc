SHELL := /bin/bash

.PHONY: test check

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

check:
	python3 -m py_compile tools/project_context.py tests/test_project_context.py
	$(MAKE) test
