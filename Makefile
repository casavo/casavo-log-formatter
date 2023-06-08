.PHONY: test fmt requirements upload upgrade-deps

test:
	nox

fmt:
	black src tests
	isort src tests
	ruff src tests

requirements:
	pip-compile --allow-unsafe --resolver=backtracking --extra dev

upgrade-deps:
	pip-compile --upgrade --allow-unsafe --resolver=backtracking --extra dev

upload:
	python -m build
	twine upload dist/*
