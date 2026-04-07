"""STUB: LLM-as-judge evaluation pattern.

Demonstrates using a language model to score open-ended responses
with model_graded_qa() and custom grading templates.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import generate

# STUB: Replace with your grading template
# The template receives {question}, {answer}, {criterion} variables
GRADING_TEMPLATE = """
You are evaluating an AI assistant's response to a question.

Question: {question}
AI Response: {answer}
Reference Answer: {criterion}

Evaluate whether the AI's response is correct and complete.
Consider:
1. Factual accuracy compared to the reference answer
2. Completeness of the response
3. Clarity and coherence

Grade the response as:
- GRADE: C (Correct) if the response is factually accurate and reasonably complete
- GRADE: I (Incorrect) if the response contains errors or is missing key information
""".strip()


@task
def llm_judge() -> Task:
    """STUB: Replace with your task description.

    This evaluation uses an LLM judge to score open-ended responses.
    The judge model can be configured via model roles:

        inspect eval my_eval/llm_judge --model openai/gpt-4o --model-roles judge=anthropic/claude-sonnet-4-20250514
    """
    # STUB: Replace with your dataset (from HuggingFace, CSV, etc.)
    dataset = [
        Sample(
            input="Explain the difference between a stack and a queue.",
            target="A stack follows LIFO (Last In, First Out) order, while a queue follows FIFO (First In, First Out) order.",
            id="ds_1",
        ),
        Sample(
            input="What is the time complexity of binary search?",
            target="O(log n) where n is the number of elements in the sorted array.",
            id="ds_2",
        ),
    ]

    return Task(
        dataset=dataset,
        solver=generate(),
        scorer=model_graded_qa(
            template=GRADING_TEMPLATE,
            # STUB: The judge model defaults to the task model.
            # Override via CLI: --model-roles judge=<model>
        ),
    )
