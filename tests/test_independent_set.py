"""Tests for Independent Set. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import IndependentSet, InvalidInstance, check_problem

TRIANGLE = [[0, 1], [1, 2], [0, 2]]


def test_interface():
    counts = check_problem(IndependentSet)
    assert counts["enumerated"] == 6505  # graphs on 0..5 vertices, k = 0..n


@pytest.mark.parametrize(
    "n, edges, k, expected",
    [
        (3, TRIANGLE, 1, True),
        (3, TRIANGLE, 2, False),
        (3, [[0, 1], [1, 2]], 2, True),   # path: endpoints
        (3, [], 3, True),                 # no edges
        (0, [], 0, True),
        (3, TRIANGLE, -1, True),          # k <= 0
        (3, [], 4, False),                # k > n
    ],
)
def test_hand_checked(n, edges, k, expected):
    instance = {"n": n, "edges": edges, "k": k}
    IndependentSet.validate(instance)
    assert IndependentSet.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in IndependentSet.enumerate_instances(IndependentSet.exhaustive_scale):
        assert IndependentSet.is_yes(instance) == reference.independent_set(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = IndependentSet.random_instance(rng, rng.randint(5, 10))
        assert IndependentSet.is_yes(instance) == reference.independent_set(**instance)


@pytest.mark.parametrize(
    "instance",
    [reference.with_k(g) for g in reference.MALFORMED_GRAPHS]
    + [
        {"n": 3, "edges": []},                 # missing k
        {"n": 3, "edges": [], "k": True},      # bool k
        {"n": 3, "edges": [], "k": "2"},       # string k
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        IndependentSet.validate(instance)


def test_size():
    assert IndependentSet.size({"n": 3, "edges": TRIANGLE, "k": 1}) == 6
