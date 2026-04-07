"""USER: Replace with your evaluation tests.

See reference/stubs/ for example test patterns.
"""

from inspect_ai import eval

from my_eval import my_eval


def test_my_eval_end_to_end() -> None:
    """End-to-end test with mock model responses."""
    [log] = eval(
        tasks=my_eval(),
        model="mockllm/model",
    )
    assert log.status == "success"
