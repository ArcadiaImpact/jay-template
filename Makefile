# MANAGED FILE - Do not edit. Updates pulled from template. See MANAGED_FILES.md

hooks:
	pre-commit install

check:
	uv run ruff format
	uv run ruff check --fix
	uv run mypy src tests
	uv lock --check
	pre-commit run markdownlint-fix --all-files

TEST_ARGS ?=
test:
	uv run pytest $(TEST_ARGS)

.PHONY: hooks check test
