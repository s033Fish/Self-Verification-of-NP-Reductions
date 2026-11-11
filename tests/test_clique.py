"""Tests for Clique. Run with: uv run pytest"""

from __future__ import annotations

import random
from itertools import combinations

import pytest
import reference

from benchmark.problems import Clique, InvalidInstance, check_problem

TRIANGLE = [[0, 1], [1, 2], [0, 2]]
K4 = [list(pair) for pair in combinations(range(4), 2)]


def test_interface():
    counts = check_problem(Clique)
    assert counts["enumerated"] == 6505


@pytest.mark.parametrize(
    "n, edges, k, expected",
    [
        (3, TRIANGLE, 3, True),
        (3, [[0, 1], [1, 2]], 3, False),  # path has no triangle
        (4, K4, 4, True),
        (1, [], 1, True),                 # a single vertex is a clique
        (3, [], 2, False),                # no edges, k = 2
        (0, [], 0, True),                 # k <= 0
        (3, TRIANGLE, 4, False),          # k > n
    ],
)
def test_hand_checked(n, edges, k, expected):
    instance = {"n": n, "edges": edges, "k": k}
    Clique.validate(instance)
    assert Clique.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in Clique.enumerate_instances(Clique.exhaustive_scale):
        assert Clique.is_yes(instance) == reference.clique(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = Clique.random_instance(rng, rng.randint(5, 10))
        assert Clique.is_yes(instance) == reference.clique(**instance)


@pytest.mark.parametrize(
    "instance",
    [reference.with_k(g) for g in reference.MALFORMED_GRAPHS]
    + [{"n": 3, "edges": []}, {"n": 3, "edges": [], "k": False}],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        Clique.validate(instance)


def test_size():
    assert Clique.size({"n": 4, "edges": K4, "k": 4}) == 10
