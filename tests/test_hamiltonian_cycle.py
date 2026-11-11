"""Tests for Hamiltonian Cycle. Run with: uv run pytest"""

from __future__ import annotations

import random
from itertools import combinations

import pytest
import reference

from benchmark.problems import HamiltonianCycle, InvalidInstance, check_problem

TRIANGLE = [[0, 1], [1, 2], [0, 2]]
C4 = [[0, 1], [1, 2], [2, 3], [3, 0]]
K4 = [list(pair) for pair in combinations(range(4), 2)]


def test_interface():
    counts = check_problem(HamiltonianCycle)
    assert counts["enumerated"] == 1100


@pytest.mark.parametrize(
    "n, edges, expected",
    [
        (0, [], False),
        (1, [], False),
        (2, [[0, 1]], False),             # no cycle on 2 vertices
        (3, TRIANGLE, True),
        (3, [[0, 1], [1, 2]], False),     # path
        (4, C4, True),
        (4, K4, True),
        (4, [[0, 1], [0, 2], [0, 3]], False),  # star
        (5, C4 + [[3, 4]], False),        # pendant vertex
    ],
)
def test_hand_checked(n, edges, expected):
    instance = {"n": n, "edges": edges}
    HamiltonianCycle.validate(instance)
    assert HamiltonianCycle.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in HamiltonianCycle.enumerate_instances(HamiltonianCycle.exhaustive_scale):
        assert HamiltonianCycle.is_yes(instance) == reference.hamiltonian_cycle(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(200):
        instance = HamiltonianCycle.random_instance(rng, rng.randint(5, 8))
        assert HamiltonianCycle.is_yes(instance) == reference.hamiltonian_cycle(**instance)


@pytest.mark.parametrize(
    "instance", reference.MALFORMED_GRAPHS + [{"n": 3, "edges": [], "k": 1}]
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        HamiltonianCycle.validate(instance)


def test_size():
    assert HamiltonianCycle.size({"n": 4, "edges": C4}) == 8
