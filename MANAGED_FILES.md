# Managed Files

This repository separates files into **managed** and **user-owned** categories.

## What are managed files?

Managed files are maintained by the template maintainers and may be updated via the [sync mechanism](#sync-mechanism). They contain CI workflows, quality standards, linter configs, Claude skills, and shared tooling. You should not edit these files — your changes will be overwritten when the template syncs.

## What are user-owned files?

User-owned files are yours to create, edit, and maintain. They contain your evaluation code, tests, README, and eval metadata. The sync mechanism will never touch these files.

## Managed file list

<!-- MANAGED_FILES_START -->

- `.claude/settings.json`
- `.claude/skills/check-trajectories-workflow/SKILL.md`
- `.claude/skills/ci-maintenance-workflow/SKILL.md`
- `.claude/skills/create-eval/SKILL.md`
- `.claude/skills/ensure-test-coverage/SKILL.md`
- `.claude/skills/eval-quality-workflow/SKILL.md`
- `.claude/skills/eval-report-workflow/SKILL.md`
- `.claude/skills/eval-validity-review/SKILL.md`
- `.claude/skills/investigate-dataset/SKILL.md`
- `.claude/skills/prepare-submission-workflow/SKILL.md`
- `.claude/skills/read-eval-logs/SKILL.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/actions/claude-setup/action.yaml`
- `.github/workflows/checks.yml`
- `.github/workflows/claude-fix-tests.yaml`
- `.github/workflows/claude-issue-solver.yaml`
- `.github/workflows/claude-review.yaml`
- `.github/workflows/lint-new-evals.yml`
- `.github/workflows/markdown-lint.yml`
- `.github/workflows/pr-template-check.yml`
- `.github/workflows/sync-template.yml`
- `.markdownlint.yaml`
- `.pre-commit-config.yaml`
- `.template-version`
- `AGENTS.md`
- `BEST_PRACTICES.md`
- `CONTRIBUTING.md`
- `EVALUATION_CHECKLIST.md`
- `MANAGED_FILES.md`
- `Makefile`
- `TASK_VERSIONING.md`
- `reference/stubs/README.md`
- `reference/stubs/agentic/`
- `reference/stubs/llm_judge/`
- `reference/stubs/simple_qa/`
- `tests/conftest.py`
- `tools/check_posix_code.py`

<!-- MANAGED_FILES_END -->

## User-owned files

These are yours — the sync mechanism will never modify them:

- `src/` — your evaluation source code
- `tests/<your_eval>/` — your tests
- `README.md` — your evaluation's documentation
- `pyproject.toml` — your project configuration (tool configs are managed, but `[project]` and `[project.entry-points]` sections are yours)
- `agent_artefacts/` — runtime artefacts from agent workflows
- `LICENSE` — your chosen license

## Sync mechanism

The `.github/workflows/sync-template.yml` workflow runs weekly (or on manual trigger) and:

1. Fetches the latest template from the upstream repository
2. Compares only managed files (listed above) with the upstream versions
3. Opens a PR if any managed files have changed
4. Your user-owned files are never touched

To manually trigger a sync, go to Actions > Sync Template Updates > Run workflow.

## What if I need to customize a managed file?

If you need to customize a managed file (e.g., add a custom ruff rule):

1. Make your change locally
2. When the sync PR arrives, review it carefully — your customization will be shown as a conflict
3. Resolve the conflict by keeping your customization where needed
4. Consider opening an issue on the template repo if your customization would benefit all users

## Template version

The current template version is tracked in `.template-version`. This file is updated when managed files change materially.
