"""STUB: Agentic evaluation pattern with Docker sandbox.

Demonstrates an agent-based evaluation where the model uses tools
in a sandboxed Docker environment. Based on patterns from SWE-bench
and CTF evaluations in inspect_evals.
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import basic_agent, system_message
from inspect_ai.tool import bash, python

# STUB: System prompt for the agent
SYSTEM_PROMPT = """
You are a helpful assistant that solves tasks by writing and executing code.
You have access to a bash shell and Python interpreter in a sandboxed environment.

When you have found the answer, submit it by printing: ANSWER: <your answer>
""".strip()

# STUB: Default message limit for agent interactions
DEFAULT_MESSAGE_LIMIT = 30

COMPOSE_FILE = str(Path(__file__).parent / "compose.yaml")


@task
def agentic_eval(
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
) -> Task:
    """STUB: Replace with your agentic task description.

    Args:
        message_limit: Maximum number of messages in the agent conversation.
    """
    # STUB: Replace with your dataset
    dataset = [
        Sample(
            input="Find the sum of all prime numbers less than 20.",
            target="77",
            id="primes_sum",
        ),
        Sample(
            input="Count the number of files in the /tmp directory.",
            target="0",
            id="count_files",
        ),
    ]

    return Task(
        dataset=dataset,
        solver=[
            system_message(SYSTEM_PROMPT),
            basic_agent(
                tools=[bash(), python()],
                message_limit=message_limit,
            ),
        ],
        scorer=includes(),
        sandbox=("docker", COMPOSE_FILE),
    )
