"""Tests for 3-SAT. Run with: uv run pytest"""

from __future__ import annotations

import random
from itertools import product

import pytest

from benchmark.problems.base import InvalidInstance, check_problem
from benchmark.problems.three_sat import ThreeSat


ALL_EIGHT_CLAUSES = [[a * 1, b * 2, c * 3] for a, b, c in product((1, -1), repeat=3)]


def brute_force(instance: dict) -> bool:
    """Try every assignment: the reference the DPLL solver is checked against."""
    for values in product((False, True), repeat=instance["num_vars"]):
        if all(
            any(values[abs(literal) - 1] == (literal > 0) for literal in clause)
            for clause in instance["clauses"]
        ):
            return True
    return False


def test_interface():
    counts = check_problem(ThreeSat)
    # m = 0, 1, 2: only the empty formula; m = 3: all 2^8 sets of the 8 clauses.
    assert counts == {"enumerated": 259, "yes": 258, "no": 1}


@pytest.mark.parametrize(
    "clauses, num_vars, expected",
    [
        ([], 0, True),                                   # empty formula
        ([[1, 2, 3]], 3, True),
        ([[1, 2, 3], [-1, -2, -3]], 3, True),
        (ALL_EIGHT_CLAUSES, 3, False),                    # every clause on 3 variables
        ([[1, 2, 3], [1, 2, 3]], 3, True),               # repeated clause is fine
    ],
)
def test_hand_checked(clauses, num_vars, expected):
    instance = {"num_vars": num_vars, "clauses": clauses}
    ThreeSat.validate(instance)
    assert ThreeSat.is_yes(instance) is expected


def test_dpll_matches_brute_force_on_enumeration():
    for instance in ThreeSat.enumerate_instances(3):
        assert ThreeSat.is_yes(instance) == brute_force(instance)


def test_dpll_matches_brute_force_on_random_instances():
    rng = random.Random(0)
    answers = []
    for _ in range(400):
        instance = ThreeSat.random_instance(rng, rng.randint(3, 8))
        answer = ThreeSat.is_yes(instance)
        assert answer == brute_force(instance)
        answers.append(answer)
    # Random instances must supply plenty of both answers.
    assert 0.2 < sum(answers) / len(answers) < 0.8


@pytest.mark.parametrize(
    "instance",
    [
        {"num_vars": 3, "clauses": [[1, 2]]},            # 2 literals
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},      # 4 literals
        {"num_vars": 3, "clauses": [[1, 1, 2]]},         # repeated variable
        {"num_vars": 3, "clauses": [[1, -1, 2]]},        # v and -v
        {"num_vars": 2, "clauses": [[1, 2, 3]]},         # variable out of range
        {"num_vars": 3, "clauses": [[0, 1, 2]]},         # literal 0
        {"num_vars": 3, "clauses": [[1, 2, True]]},      # bool literal
        {"num_vars": 3},                                 # missing key
        {"num_vars": 3, "clauses": [], "k": 1},          # extra key
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        ThreeSat.validate(instance)


def test_size():
    assert ThreeSat.size({"num_vars": 4, "clauses": [[1, 2, 3], [-2, 3, 4]]}) == 10