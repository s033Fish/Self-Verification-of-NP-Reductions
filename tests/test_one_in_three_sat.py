"""Tests for 1-in-3-SAT. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import InvalidInstance, OneInThreeSat, check_problem


def test_interface():
    counts = check_problem(OneInThreeSat)
    # m <= 2: 1 each; m = 3: 2; m = 4: 2^4; m = 5: 2^10.
    assert counts["enumerated"] == 3 + 2 + 16 + 1024


@pytest.mark.parametrize(
    "num_vars, clauses, expected",
    [
        (0, [], True),
        (3, [[1, 2, 3]], True),
        (3, [[1, 2, 3], [1, 2, 3]], True),            # repeated clause
        (6, [[1, 2, 3], [4, 5, 6]], True),
        # Each variable is in 3 of the 4 clauses: 3 * (true count) = 4 is impossible.
        (4, [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]], False),
    ],
)
def test_hand_checked(num_vars, clauses, expected):
    instance = {"num_vars": num_vars, "clauses": clauses}
    OneInThreeSat.validate(instance)
    assert OneInThreeSat.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in OneInThreeSat.enumerate_instances(OneInThreeSat.exhaustive_scale):
        assert OneInThreeSat.is_yes(instance) == reference.one_in_three(
            instance["num_vars"], instance["clauses"]
        )


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = OneInThreeSat.random_instance(rng, rng.randint(3, 10))
        assert OneInThreeSat.is_yes(instance) == reference.one_in_three(
            instance["num_vars"], instance["clauses"]
        )


@pytest.mark.parametrize(
    "instance",
    [
        {"num_vars": 3, "clauses": [[-1, 2, 3]]},    # negative literal
        {"num_vars": 3, "clauses": [[1, 2]]},        # 2 variables
        {"num_vars": 3, "clauses": [[1, 1, 2]]},     # repeated variable
        {"num_vars": 2, "clauses": [[1, 2, 3]]},     # out of range
        {"num_vars": 3, "clauses": [], "k": 1},      # extra key
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        OneInThreeSat.validate(instance)


def test_size():
    assert OneInThreeSat.size({"num_vars": 4, "clauses": [[1, 2, 3]]}) == 8
