"""STUB: Tests for the simple Q&A evaluation.

Demonstrates the required test patterns:
1. test_record_to_sample — Unit test for data conversion
2. test_end_to_end — E2E test with mockllm
3. test_end_to_end_correct — E2E test with custom mock responses
"""

import pytest
from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model

from reference.stubs.simple_qa.simple_qa import record_to_sample, simple_qa


def test_record_to_sample() -> None:
    """Test that record_to_sample correctly converts a dataset record.

    STUB: Use an actual example from your dataset to serve as both
    a test and documentation of the expected format.
    """
    record = {
        "question": "What is 2 + 2?",
        "answer": "2 + 2 equals 4\n#### 4",
        "id": "test_1",
    }
    sample = record_to_sample(record)
    assert sample.input == "What is 2 + 2?"
    assert sample.target == "4"
    assert sample.id == "test_1"
    assert sample.metadata is not None
    assert "full_answer" in sample.metadata


@pytest.mark.dataset_download
@pytest.mark.huggingface
def test_end_to_end() -> None:
    """E2E test with default mock responses.

    Confirms the pipeline runs without errors. All responses will
    presumably be incorrect since mockllm returns generic text.
    """
    [log] = eval(
        tasks=simple_qa(),
        model="mockllm/model",
        limit=2,
    )
    assert log.status == "success"


@pytest.mark.dataset_download
@pytest.mark.huggingface
def test_end_to_end_correct() -> None:
    """E2E test with a custom mock response that should score correctly.

    STUB: Adapt the mock response to match what your scorer expects.
    """
    [log] = eval(
        tasks=simple_qa(),
        model=get_model(
            "mockllm/model",
            custom_outputs=[
                ModelOutput.from_content(
                    model="mockllm/model",
                    content="Let me solve this step by step.\n\nANSWER: 2",
                ),
            ],
        ),
        limit=1,
    )
    assert log.status == "success"
