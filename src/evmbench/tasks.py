r"""EVMbench: Evaluating AI Agents on Smart Contract Security.

Three task types:
- evmbench_detect: Find vulnerabilities in smart contract codebases
- evmbench_patch: Fix identified vulnerabilities
- evmbench_exploit: Exploit deployed vulnerable contracts

Each task supports dual versions via config:
- Default ("improved"): Tuned prompts, tool-calling scorer, practical limits
- Paper-faithful ("original"): Exact reference prompts, string-matching scorer

For paper-faithful reproduction, use --task-config:

    inspect eval evmbench/evmbench_detect \
        --task-config src/evmbench/paper_config/evmbench.yaml \
        --model openai/gpt-5.1-2025-11-13

For provider-specific agent behavior (Python only):

    from inspect_ai import eval, task_with
    from inspect_swe import claude_code
    from evmbench import evmbench_detect

    eval(
        task_with(
            evmbench_detect(scorer="original", prompt_mode="original"),
            solver=claude_code(model="claude-opus-4-1"),
        ),
        model="anthropic/claude-opus-4-1",
    )
"""

from inspect_ai import Task, task
from inspect_ai.scorer import Scorer
from inspect_ai.solver import basic_agent, system_message
from inspect_ai.tool import bash, python, text_editor

from evmbench.constants import DEFAULT_MESSAGE_LIMIT, DEFAULT_TIME_LIMIT_HOURS
from evmbench.dataset import load_evmbench_dataset
from evmbench.prompts import PromptMode, get_prompt
from evmbench.scorers import ScorerChoice, detect_scorer, exploit_scorer, patch_scorer
from utils.metadata import load_version_from_yaml

EVAL_VERSION = load_version_from_yaml("evmbench")


def _resolve_detect_scorer(scorer_choice: ScorerChoice) -> Scorer:
    """Return the appropriate detect scorer based on the choice.

    Args:
        scorer_choice: "tool" for structured grading (default),
            "original" for string-matching grading.
    """
    return detect_scorer(mode=scorer_choice)


@task
def evmbench_detect(
    scorer: ScorerChoice = "tool",
    prompt_mode: PromptMode = "improved",
    split: str | None = None,
    audit_ids: list[str] | None = None,
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
    time_limit_hours: float = DEFAULT_TIME_LIMIT_HOURS,
) -> Task:
    r"""EVMbench vulnerability detection task.

    Agents audit smart contract codebases and produce vulnerability reports.
    Scored by comparing the agent's findings against ground truth using an
    LLM grader.

    For paper-faithful reproduction::

        inspect eval evmbench/evmbench_detect \\
            --task-config src/evmbench/paper_config/evmbench.yaml \\
            --model openai/gpt-5.1-2025-11-13

    Args:
        scorer: "tool" (default) uses structured tool-calling grader;
            "original" uses string-matching grader.
        prompt_mode: "improved" (default) or "original" for paper's exact
            instruction templates.
        split: Optional split file name for filtering (e.g., "detect-tasks").
        audit_ids: Optional list of specific audit IDs to evaluate.
        message_limit: Maximum agent messages (default 200).
        time_limit_hours: Per-sample time limit in hours (default 1, paper 6).
    """
    dataset = load_evmbench_dataset("detect", prompt_mode, split, audit_ids)
    return Task(
        dataset=dataset,
        solver=basic_agent(
            init=system_message(get_prompt("detect", prompt_mode)),
            tools=[bash(timeout=180), python(timeout=180)],
            message_limit=message_limit,
        ),
        scorer=_resolve_detect_scorer(scorer),
        time_limit=int(time_limit_hours * 3600),
        version=EVAL_VERSION,
    )


@task
def evmbench_patch(
    prompt_mode: PromptMode = "improved",
    split: str | None = None,
    audit_ids: list[str] | None = None,
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
    time_limit_hours: float = DEFAULT_TIME_LIMIT_HOURS,
) -> Task:
    r"""EVMbench vulnerability patching task.

    Agents fix identified vulnerabilities in smart contracts. Scored by
    running the vulnerability-specific test: a correct patch causes the
    exploit test to fail.

    For paper-faithful reproduction::

        inspect eval evmbench/evmbench_patch \\
            --task-config src/evmbench/paper_config/evmbench.yaml \\
            --model openai/gpt-5.1-2025-11-13

    Args:
        prompt_mode: "improved" (default) or "original" for paper's exact
            instruction templates.
        split: Optional split file name for filtering (e.g., "patch-tasks").
        audit_ids: Optional list of specific audit IDs to evaluate.
        message_limit: Maximum agent messages (default 200).
        time_limit_hours: Per-sample time limit in hours (default 1, paper 6).
    """
    dataset = load_evmbench_dataset("patch", prompt_mode, split, audit_ids)
    return Task(
        dataset=dataset,
        solver=basic_agent(
            init=system_message(get_prompt("patch", prompt_mode)),
            tools=[bash(timeout=180), python(timeout=180), text_editor()],
            message_limit=message_limit,
        ),
        scorer=patch_scorer(),
        time_limit=int(time_limit_hours * 3600),
        version=EVAL_VERSION,
    )


@task
def evmbench_exploit(
    prompt_mode: PromptMode = "improved",
    split: str | None = None,
    audit_ids: list[str] | None = None,
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
    time_limit_hours: float = DEFAULT_TIME_LIMIT_HOURS,
) -> Task:
    r"""EVMbench vulnerability exploitation task.

    Agents exploit deployed vulnerable contracts on a local Ethereum testnet.
    Scored by running grading scripts that check balance changes.

    For paper-faithful reproduction::

        inspect eval evmbench/evmbench_exploit \\
            --task-config src/evmbench/paper_config/evmbench.yaml \\
            --model openai/gpt-5.1-2025-11-13

    Args:
        prompt_mode: "improved" (default) or "original" for paper's exact
            instruction templates.
        split: Optional split file name for filtering (e.g., "exploit-tasks").
        audit_ids: Optional list of specific audit IDs to evaluate.
        message_limit: Maximum agent messages (default 200).
        time_limit_hours: Per-sample time limit in hours (default 1, paper 6).
    """
    dataset = load_evmbench_dataset("exploit", prompt_mode, split, audit_ids)
    return Task(
        dataset=dataset,
        solver=basic_agent(
            init=system_message(get_prompt("exploit", prompt_mode)),
            tools=[bash(timeout=180), python(timeout=180)],
            message_limit=message_limit,
        ),
        scorer=exploit_scorer(),
        time_limit=int(time_limit_hours * 3600),
        version=EVAL_VERSION,
    )
