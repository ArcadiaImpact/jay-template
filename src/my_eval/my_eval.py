"""USER: Replace this with your evaluation implementation.

See reference/stubs/ for example patterns:
- simple_qa/  — Simple Q&A with dataset and match scoring
- llm_judge/  — LLM-as-judge scoring
- agentic/    — Agentic eval with Docker sandbox
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate


@task
def my_eval() -> Task:
    """USER: Replace with your evaluation task."""
    dataset = [
        Sample(
            input="What is the capital of France?",
            target="Paris",
        ),
    ]

    return Task(
        dataset=dataset,
        solver=generate(),
        scorer=match(),
    )
