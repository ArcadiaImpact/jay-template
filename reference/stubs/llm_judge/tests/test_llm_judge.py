"""STUB: Tests for the LLM-as-judge evaluation.

Demonstrates testing patterns for model-graded scoring:
1. E2E test with mockllm (judge model also mocked)
2. Testing correct and incorrect scoring paths
"""

from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model
from inspect_ai.scorer import CORRECT, INCORRECT

from reference.stubs.llm_judge.llm_judge import llm_judge


def test_end_to_end() -> None:
    """E2E test with default mock responses.

    Both the solver and judge use mockllm, so the judge will return
    generic text. This tests that the pipeline completes without errors.
    """
    [log] = eval(
        tasks=llm_judge(),
        model="mockllm/model",
    )
    assert log.status == "success"


def test_correct_grading() -> None:
    """Test that a correct grade is properly scored.

    STUB: The mock judge response should match what model_graded_qa
    expects for a correct answer (GRADE: C).
    """
    [log] = eval(
        tasks=llm_judge(),
        model=get_model(
            "mockllm/model",
            custom_outputs=[
                # Solver response
                ModelOutput.from_content(
                    model="mockllm/model",
                    content="A stack uses LIFO, a queue uses FIFO.",
                ),
                # Judge response
                ModelOutput.from_content(
                    model="mockllm/model",
                    content="GRADE: C",
                ),
            ],
        ),
        limit=1,
    )
    assert log.status == "success"
    assert log.results is not None
    scores = log.results.scores
    assert len(scores) > 0
    sample_score = log.samples[0].scores["model_graded_qa"]
    assert sample_score.value == CORRECT


def test_incorrect_grading() -> None:
    """Test that an incorrect grade is properly scored."""
    [log] = eval(
        tasks=llm_judge(),
        model=get_model(
            "mockllm/model",
            custom_outputs=[
                # Solver response
                ModelOutput.from_content(
                    model="mockllm/model",
                    content="They are the same thing.",
                ),
                # Judge response
                ModelOutput.from_content(
                    model="mockllm/model",
                    content="GRADE: I",
                ),
            ],
        ),
        limit=1,
    )
    assert log.status == "success"
    sample_score = log.samples[0].scores["model_graded_qa"]
    assert sample_score.value == INCORRECT
