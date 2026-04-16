"""End-to-end tests for EVMbench evaluation tasks."""

import pytest
from inspect_ai import Task

from evmbench.tasks import evmbench_detect, evmbench_exploit, evmbench_patch
from evmbench.prompts import get_prompt


def test_get_prompt_detect_original() -> None:
    prompt = get_prompt("detect", "original")
    assert "expert security researcher" in prompt
    assert "submission/audit.md" in prompt


def test_get_prompt_detect_improved() -> None:
    prompt = get_prompt("detect", "improved")
    assert "audit" in prompt.lower()


def test_get_prompt_patch_original() -> None:
    prompt = get_prompt("patch", "original")
    assert "fix vulnerabilities" in prompt.lower()


def test_get_prompt_exploit_original() -> None:
    prompt = get_prompt("exploit", "original")
    assert "exploit smart contracts" in prompt.lower()


@pytest.mark.dataset_download
def test_evmbench_detect_returns_task() -> None:
    """Verify evmbench_detect returns a Task with real dataset."""
    task = evmbench_detect.__wrapped__(
        scorer="tool",
        prompt_mode="improved",
        message_limit=3,
        time_limit_hours=0.01,
    )
    assert isinstance(task, Task)


@pytest.mark.dataset_download
def test_evmbench_patch_returns_task() -> None:
    task = evmbench_patch.__wrapped__(
        prompt_mode="improved",
        message_limit=3,
        time_limit_hours=0.01,
    )
    assert isinstance(task, Task)


@pytest.mark.dataset_download
def test_evmbench_exploit_returns_task() -> None:
    """Exploit task may have no samples if no exploit_task=True in dataset."""
    try:
        task = evmbench_exploit.__wrapped__(
            prompt_mode="improved",
            message_limit=3,
            time_limit_hours=0.01,
        )
        assert isinstance(task, Task)
    except ValueError as e:
        if "empty" in str(e).lower():
            pytest.skip("No exploit samples available in downloaded dataset")
        raise
