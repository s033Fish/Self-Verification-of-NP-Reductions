"""Checks on the problem registry and the specs agents read.

Run with: uv run pytest
"""

from __future__ import annotations

import time

import pytest

from benchmark.problems import PROBLEMS, Problem


def test_all_fifteen_problems_are_registered():
    assert len(PROBLEMS) == 15
    assert len({problem.name for problem in PROBLEMS.values()}) == 15


@pytest.mark.parametrize("key", sorted(PROBLEMS))
def test_docstring_states_the_full_spec(key):
    """Agents only see the docstring, so it must give the format, the
    yes-condition and the edge cases."""
    doc = PROBLEMS[key].__doc__ or ""
    assert "Instance:" in doc
    assert "Yes iff" in doc
    assert "Edge cases:" in doc


@pytest.mark.parametrize("key", sorted(PROBLEMS))
def test_exhaustive_check_is_fast(key):
    """The verifier runs every enumerated instance through is_yes; keep the
    exhaustive scale small enough for that to take seconds, not minutes."""
    problem: type[Problem] = PROBLEMS[key]
    start = time.monotonic()
    for instance in problem.enumerate_instances(problem.exhaustive_scale):
        problem.is_yes(instance)
    assert time.monotonic() - start < 10
