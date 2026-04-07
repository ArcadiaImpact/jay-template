"""STUB: Simple Q&A evaluation pattern.

Demonstrates loading a HuggingFace dataset, converting records to samples,
applying a prompt template, and scoring with match().

Based on the GSM8K and GPQA evaluation patterns from inspect_evals.
"""

from typing import Any

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate, prompt_template, system_message

# STUB: Replace with your HuggingFace dataset path
DATASET_PATH = "openai/gsm8k"

# STUB: Pin to a specific dataset revision for reproducibility
# Find the revision SHA at: https://huggingface.co/api/datasets/<path>
DATASET_REVISION = "cc7b047b6e5bb11b4f1af84efc572db110a51b3c"

# STUB: Replace with your prompt template
PROMPT_TEMPLATE = """
Solve the following problem. The last line of your response should be
of the form "ANSWER: $ANSWER" where $ANSWER is your final answer.

{prompt}

ANSWER:
""".strip()

# STUB: Define few-shot examples if needed
FEWSHOT_EXAMPLES = """
Example: What is 2 + 3?
ANSWER: 5

Example: What is 10 - 4?
ANSWER: 6
""".strip()

# STUB: Default number of few-shot examples (0 to disable)
DEFAULT_FEWSHOT = 0

# STUB: Default number of epochs
DEFAULT_EPOCHS = 1


@task
def simple_qa(
    fewshot: int = DEFAULT_FEWSHOT,
    epochs: int = DEFAULT_EPOCHS,
) -> Task:
    """STUB: Replace with your task description.

    Args:
        fewshot: Number of few-shot examples to include.
        epochs: Number of evaluation epochs.
    """
    # STUB: Import here to avoid import-time side effects
    from inspect_evals.utils.huggingface import hf_dataset

    solver = [prompt_template(PROMPT_TEMPLATE), generate()]
    if fewshot:
        solver.insert(0, system_message(FEWSHOT_EXAMPLES))

    return Task(
        dataset=hf_dataset(
            path=DATASET_PATH,
            split="test",
            sample_fields=record_to_sample,
            revision=DATASET_REVISION,
        ),
        solver=solver,
        scorer=match(numeric=True),
        epochs=epochs,
    )


def record_to_sample(record: dict[str, Any]) -> Sample:
    """STUB: Convert a dataset record to an Inspect Sample.

    This function maps raw dataset fields to the Sample format.
    Update field names to match your dataset's schema.
    """
    # STUB: Adapt these field names to your dataset
    return Sample(
        input=record["question"],
        target=record["answer"].split("####")[-1].strip(),
        id=str(record.get("id", "")),
        metadata={
            # STUB: Include useful metadata for debugging and analysis
            "full_answer": record["answer"],
        },
    )
