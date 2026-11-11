"""Tests for Dominating Set. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import DominatingSet, InvalidInstance, check_problem

STAR = [[0, 1], [0, 2], [0, 3]]
PATH4 = [[0, 1], [1, 2], [2, 3]]


def test_interface():
    counts = check_problem(DominatingSet)
    assert counts["enumerated"] == 6505


@pytest.mark.parametrize(
    "n, edges, k, expected",
    [
        (4, STAR, 1, True),               # the centre dominates everything
        (4, PATH4, 1, False),
        (4, PATH4, 2, True),              # vertices 1 and 2
        (3, [], 2, False),                # isolated vertices must all be chosen
        (3, [], 3, True),
        (0, [], 0, True),
        (4, STAR, -1, False),             # k < 0
    ],
)
def test_hand_checked(n, edges, k, expected):
    instance = {"n": n, "edges": edges, "k": k}
    DominatingSet.validate(instance)
    assert DominatingSet.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in DominatingSet.enumerate_instances(DominatingSet.exhaustive_scale):
        assert DominatingSet.is_yes(instance) == reference.dominating_set(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = DominatingSet.random_instance(rng, rng.randint(5, 10))
        assert DominatingSet.is_yes(instance) == reference.dominating_set(**instance)


@pytest.mark.parametrize(
    "instance",
    [reference.with_k(g) for g in reference.MALFORMED_GRAPHS]
    + [{"n": 3, "edges": []}, {"n": 3, "edges": [], "k": None}],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        DominatingSet.validate(instance)


def test_size():
    assert DominatingSet.size({"n": 4, "edges": PATH4, "k": 2}) == 7
