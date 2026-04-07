"""STUB: Tests for the agentic evaluation.

Demonstrates testing patterns for agent-based evaluations:
1. E2E test with Docker sandbox (marked @pytest.mark.docker)
2. Unit test for scoring without Docker
"""

import pytest
from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model

from reference.stubs.agentic.agentic import agentic_eval


@pytest.mark.docker
@pytest.mark.slow(30)
def test_end_to_end() -> None:
    """E2E test that builds the Docker sandbox and runs the agent.

    This test is slow because it builds the Docker image.
    Mark with @pytest.mark.docker and @pytest.mark.slow.
    """
    [log] = eval(
        tasks=agentic_eval(message_limit=5),
        model="mockllm/model",
        limit=1,
    )
    assert log.status == "success"


def test_correct_answer_scoring() -> None:
    """Test that the scorer correctly identifies the right answer.

    Uses a mock model that immediately returns the correct answer,
    bypassing the need for Docker.
    """
    [log] = eval(
        tasks=agentic_eval(message_limit=3),
        model=get_model(
            "mockllm/model",
            custom_outputs=[
                ModelOutput.from_content(
                    model="mockllm/model",
                    content="ANSWER: 77",
                ),
            ],
        ),
        limit=1,
        sandbox=None,  # Skip Docker for unit test
    )
    assert log.status == "success"
