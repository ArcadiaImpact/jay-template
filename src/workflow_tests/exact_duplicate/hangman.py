"""Test fixture for the inspect_evals registry-submission workflow.

Declares `@task def hangman` — a name that already exists in
inspect_evals' registry/hangman-bench/ entry. A registry-submission PR
pointing here with `tasks[0].name: hangman` must be blocked by the
automated duplicate check before Claude's review runs.

The task is intentionally valid (minimal dataset + scorer), so that if
the duplicate check were ever disabled or bypassed, Claude's task-
function/runnability checks would still pass. The collision detection
is the single failure mode being exercised.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate


@task
def hangman() -> Task:
    return Task(
        dataset=[Sample(input="What is 1+1?", target="2")],
        solver=[generate()],
        scorer=match(),
    )
