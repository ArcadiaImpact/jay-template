# EVMbench

[EVMbench](https://cdn.openai.com/evmbench/evmbench.pdf) (OpenAI, 2026) evaluates AI agents on smart contract security across three tasks: vulnerability detection, patching, and exploitation. The benchmark contains 120 curated vulnerabilities from 43 real-world security audits.

## Prerequisites

- Docker (required for all tasks)
- First run builds Docker images (~10 min for base, ~1-2 min per audit)

## Quick Start

```bash
# Default run (improved prompts, tool-calling scorer)
inspect eval evmbench/evmbench_detect --model openai/gpt-4o --limit 5
```

## Tasks

| Task | What the agent does | Scoring |
|------|-------------------|---------|
| `evmbench_detect` | Audits smart contract codebase, writes vulnerability report | LLM-graded comparison against ground truth findings |
| `evmbench_patch` | Fixes identified vulnerabilities in smart contracts | Runs exploit test in sandbox; correct patch causes test to fail |
| `evmbench_exploit` | Exploits deployed contracts on local Ethereum testnet | Runs grading scripts; checks balance changes |

## Paper-Faithful Reproduction

Use `--task-config` to apply all paper-faithful settings from a single config file:

```bash
inspect eval evmbench/evmbench_detect \
    --task-config src/evmbench/paper_config/evmbench.yaml \
    --model openai/gpt-5.1-2025-11-13
```

This sets: `scorer=original`, `prompt_mode=original`, `time_limit_hours=6`, `message_limit=200`.

For provider-specific agent behavior matching the reference implementation (Python only):

```python
from inspect_ai import eval, task_with
from inspect_swe import claude_code  # pip install inspect_swe
from evmbench import evmbench_detect

eval(
    task_with(
        evmbench_detect(scorer="original", prompt_mode="original", time_limit_hours=6),
        solver=claude_code(model="claude-opus-4-1"),
    ),
    model="anthropic/claude-opus-4-1",
)
```

## Configuration

### Task Parameters

| Parameter | Default | Paper | Description |
|-----------|---------|-------|-------------|
| `scorer` | `"tool"` | `"original"` | Detect task only. `"tool"` = structured tool-calling grader; `"original"` = string-matching |
| `prompt_mode` | `"improved"` | `"original"` | `"original"` = exact reference prompts; `"improved"` = tuned for Inspect |
| `time_limit_hours` | `1.0` | `6` | Per-sample time limit in hours |
| `message_limit` | `200` | `200` | Maximum agent messages |
| `split` | `None` | - | Filter by split file (e.g., `"detect-tasks"`, `"patch-tasks"`) |
| `audit_ids` | `None` | - | Filter to specific audit IDs |

### Configuration Layers

| Setting | Mechanism | Example |
|---------|-----------|---------|
| Task parameters | `--task-config` or `-T` | `--task-config src/evmbench/paper_config/evmbench.yaml` |
| Temperature, max_tokens | `--generate-config` | `--generate-config src/evmbench/paper_config/generate.yaml` |
| Grader model | `--model-role` | `--model-role 'grader={"model": "openai/gpt-4o"}'` |
| Solver (agent) | `task_with()` | `task_with(evmbench_detect(), solver=claude_code(...))` |

## Scoring

### Detect Task

For each ground-truth vulnerability, an LLM grader assesses whether the agent's audit report identified it. Metrics:

- **vulns_found**: Fraction of vulnerabilities correctly identified
- **award_weighted**: Award-weighted score (higher-value vulnerabilities count more)

### Patch Task

The vulnerability-specific test is run after the agent's patch is applied. A correct patch causes the exploit test to **fail** (the vulnerability is eliminated).

- Standard `accuracy` and `stderr` metrics

### Exploit Task

Grading scripts from the reference implementation check whether the agent successfully drained funds.

- **exploit_success**: Fraction of vulnerabilities successfully exploited
- **award_weighted**: Award-weighted exploitation score

## Known Limitations

1. **Agent behavior parity**: Inspect's `basic_agent` has different prompting and tool-call formatting than the reference implementation's per-provider agents. Numerical results will differ from the paper's reported scores. Use `inspect_swe` for closer replication.

2. **Docker build time**: First run requires building Docker images. The base image takes ~10 minutes; each per-audit image takes 1-2 minutes. Images are cached after the first build.

3. **Exploit task**: Requires Anvil (Ethereum testnet) running as a Docker service. More complex than detect/patch tasks.

## Reference

- Paper: <https://cdn.openai.com/evmbench/evmbench.pdf>
- Reference implementation: <https://github.com/openai/frontier-evals/tree/main/project/evmbench>
- Issue: <https://github.com/UKGovernmentBEIS/inspect_evals/issues/1133>
