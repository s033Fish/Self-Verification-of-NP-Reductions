"""Tests for SAT. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import InvalidInstance, Sat, check_problem


def test_interface():
    counts = check_problem(Sat)
    # m = 0: 2 formulas; m = 1: 2^3; m = 2: 2^9.
    assert counts["enumerated"] == 2 + 8 + 512


@pytest.mark.parametrize(
    "num_vars, clauses, expected",
    [
        (0, [], True),                   # no clauses
        (0, [[]], False),                # empty clause
        (1, [[1], [-1]], False),
        (1, [[1, -1]], True),            # tautology
        (1, [[1, 1]], True),             # repeated literal
        (2, [[1, 2], [-1], [-2]], False),
        (3, [[1, 2, 3, -1], [-2]], True),  # clause longer than 3
    ],
)
def test_hand_checked(num_vars, clauses, expected):
    instance = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(instance)
    assert Sat.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in Sat.enumerate_instances(Sat.exhaustive_scale):
        assert Sat.is_yes(instance) == reference.sat(instance["num_vars"], instance["clauses"])


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = Sat.random_instance(rng, rng.randint(0, 8))
        assert Sat.is_yes(instance) == reference.sat(instance["num_vars"], instance["clauses"])


@pytest.mark.parametrize(
    "instance",
    [
        {"num_vars": 2, "clauses": [[0]]},          # literal 0
        {"num_vars": 2, "clauses": [[3]]},          # variable out of range
        {"num_vars": 2, "clauses": [[True]]},       # bool literal
        {"num_vars": 2, "clauses": [1, 2]},         # clauses not lists
        {"num_vars": -1, "clauses": []},            # negative num_vars
        {"clauses": []},                            # missing key
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        Sat.validate(instance)


def test_size():
    # 3 variables + 2 clauses + 4 literal occurrences
    assert Sat.size({"num_vars": 3, "clauses": [[1, -2, 3], [2]]}) == 9
