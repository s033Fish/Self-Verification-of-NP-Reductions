"""Tests for Hamiltonian Path. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import HamiltonianPath, InvalidInstance, check_problem

STAR3 = [[0, 1], [0, 2], [0, 3]]


def test_interface():
    counts = check_problem(HamiltonianPath)
    assert counts["enumerated"] == 1100


@pytest.mark.parametrize(
    "n, edges, expected",
    [
        (0, [], False),
        (1, [], True),
        (2, [[0, 1]], True),
        (2, [], False),
        (4, [[0, 1], [1, 2], [2, 3]], True),
        (4, STAR3, False),                # three leaves cannot all be on a path
        (4, [[0, 1], [2, 3]], False),     # disconnected
    ],
)
def test_hand_checked(n, edges, expected):
    instance = {"n": n, "edges": edges}
    HamiltonianPath.validate(instance)
    assert HamiltonianPath.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in HamiltonianPath.enumerate_instances(HamiltonianPath.exhaustive_scale):
        assert HamiltonianPath.is_yes(instance) == reference.hamiltonian_path(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(200):
        instance = HamiltonianPath.random_instance(rng, rng.randint(5, 8))
        assert HamiltonianPath.is_yes(instance) == reference.hamiltonian_path(**instance)


@pytest.mark.parametrize(
    "instance", reference.MALFORMED_GRAPHS + [{"n": 3, "edges": [], "k": 1}]
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        HamiltonianPath.validate(instance)


def test_size():
    assert HamiltonianPath.size({"n": 4, "edges": STAR3}) == 7
