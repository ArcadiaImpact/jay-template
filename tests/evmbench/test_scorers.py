"""Tests for EVMbench scorers."""

from inspect_ai.scorer import Scorer

from evmbench.scorers import detect_scorer, exploit_scorer, patch_scorer


def test_detect_scorer_is_scorer() -> None:
    """Verify detect_scorer returns a Scorer instance."""
    result = detect_scorer(mode="tool")
    assert isinstance(result, Scorer)


def test_detect_scorer_original_is_scorer() -> None:
    result = detect_scorer(mode="original")
    assert isinstance(result, Scorer)


def test_patch_scorer_is_scorer() -> None:
    result = patch_scorer()
    assert isinstance(result, Scorer)


def test_exploit_scorer_is_scorer() -> None:
    result = exploit_scorer()
    assert isinstance(result, Scorer)
