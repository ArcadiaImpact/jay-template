# MANAGED FILE - Do not edit. Updates pulled from template. See MANAGED_FILES.md
---
name: prepare-submission-workflow
description: Prepare an evaluation for publishing — run quality checks, tests, linting, verify eval.yaml and README completeness. Use when user asks to prepare an eval for publishing or finalize before release. Trigger when the user asks you to run the "Prepare Evaluation For Publishing" workflow.
---

# Prepare Eval For Publishing

## Workflow Steps

To prepare an evaluation for publishing:

1. Add custom dependencies in the [pyproject.toml](pyproject.toml) file, if required.

   ```toml
   [project.optional-dependencies]
   your_evaluation = ["example-python-package"]

   [project]
   dependencies = [
      "inspect_ai",
      # ... other deps
   ]
   ```

   Pin the package version if your evaluation might be sensitive to version updates.

   Make sure your module does not import your custom dependencies when the module is imported. This breaks the way `inspect_ai` imports tasks from the registry.

   To check for this, `pip uninstall` your optional dependencies and run another eval with `--limit=0`. If it fails due to one of your imports, you need to change how you are importing that dependency.

2. Add pytest tests covering the custom functions included in your evaluation. See the Testing Standards section in CONTRIBUTING.md for more details.

3. Run `pytest` to ensure all new and existing tests pass.

   To install test dependencies:

   ```bash
   uv sync --extra test
   ```

   Then run the tests:

   ```bash
   uv run pytest tests/<eval_name>
   ```

4. Add an `eval.yaml` file to your evaluation directory (e.g., `src/<eval_name>/eval.yaml`) to include it in the documentation. See the eval.yaml Reference section in CONTRIBUTING.md for a complete example and field documentation.

5. Run linting, formatting, and type checking and address any issues:

   ```bash
   make check
   ```

   Note that CI automatically runs these checks, so be sure your contribution passes before publishing.

6. Fill in the missing sections of the README.md which are marked with 'TODO:'.

7. Verify the eval runs successfully with a smoke test:

   ```bash
   uv run inspect eval <eval_name>/task_name --limit 0
   ```

8. Review the overall package structure:
   - `src/<eval_name>/` contains the eval implementation
   - `tests/<eval_name>/` contains the tests
   - `eval.yaml` is present and complete
   - `README.md` is present and complete (no remaining TODOs)
   - All linting and tests pass
