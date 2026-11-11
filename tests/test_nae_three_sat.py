"""Tests for NAE-3-SAT. Run with: uv run pytest"""

from __future__ import annotations

import random
from itertools import product

import pytest
import reference

from benchmark.problems import InvalidInstance, NaeThreeSat, check_problem

ALL_EIGHT_CLAUSES = [[a * 1, b * 2, c * 3] for a, b, c in product((1, -1), repeat=3)]


def test_interface():
    counts = check_problem(NaeThreeSat)
    assert counts["enumerated"] == 259


@pytest.mark.parametrize(
    "num_vars, clauses, expected",
    [
        (0, [], True),
        (3, [[1, 2, 3]], True),
        (3, [[1, 2, 3], [-1, -2, -3]], True),  # same constraint, negated
        (3, ALL_EIGHT_CLAUSES, False),
        # Every assignment makes one of these four clauses all-equal.
        (3, [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]], False),
        (4, [[1, 2, 3], [-1, 2, 4]], True),
    ],
)
def test_hand_checked(num_vars, clauses, expected):
    instance = {"num_vars": num_vars, "clauses": clauses}
    NaeThreeSat.validate(instance)
    assert NaeThreeSat.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in NaeThreeSat.enumerate_instances(NaeThreeSat.exhaustive_scale):
        assert NaeThreeSat.is_yes(instance) == reference.nae(
            instance["num_vars"], instance["clauses"]
        )


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = NaeThreeSat.random_instance(rng, rng.randint(3, 8))
        assert NaeThreeSat.is_yes(instance) == reference.nae(
            instance["num_vars"], instance["clauses"]
        )


@pytest.mark.parametrize(
    "instance",
    [
        {"num_vars": 3, "clauses": [[1, 2]]},        # 2 literals
        {"num_vars": 3, "clauses": [[1, 1, 2]]},     # repeated variable
        {"num_vars": 3, "clauses": [[1, -1, 2]]},    # v and -v
        {"num_vars": 2, "clauses": [[1, 2, 3]]},     # out of range
        {"num_vars": 3, "clauses": [[0, 1, 2]]},     # literal 0
        {"num_vars": 3},                             # missing key
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        NaeThreeSat.validate(instance)


def test_size():
    assert NaeThreeSat.size({"num_vars": 4, "clauses": [[1, 2, 3], [-2, 3, 4]]}) == 12
