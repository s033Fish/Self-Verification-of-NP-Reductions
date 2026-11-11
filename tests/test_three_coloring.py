"""Tests for 3-Coloring. Run with: uv run pytest"""

from __future__ import annotations

import random
from itertools import combinations

import pytest
import reference

from benchmark.problems import InvalidInstance, ThreeColoring, check_problem

K4 = [list(pair) for pair in combinations(range(4), 2)]
C5 = [[i, (i + 1) % 5] for i in range(5)]
# Wheel: hub 5 joined to every vertex of the odd cycle C5 -> needs 4 colours.
WHEEL5 = C5 + [[i, 5] for i in range(5)]


def test_interface():
    counts = check_problem(ThreeColoring)
    assert counts["enumerated"] == 1100  # graphs on 0..5 vertices


@pytest.mark.parametrize(
    "n, edges, expected",
    [
        (0, [], True),
        (3, [[0, 1], [1, 2], [0, 2]], True),
        (4, K4, False),
        (5, C5, True),                    # odd cycle needs exactly 3
        (6, WHEEL5, False),
    ],
)
def test_hand_checked(n, edges, expected):
    instance = {"n": n, "edges": edges}
    ThreeColoring.validate(instance)
    assert ThreeColoring.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in ThreeColoring.enumerate_instances(ThreeColoring.exhaustive_scale):
        assert ThreeColoring.is_yes(instance) == reference.three_coloring(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = ThreeColoring.random_instance(rng, rng.randint(5, 9))
        assert ThreeColoring.is_yes(instance) == reference.three_coloring(**instance)


@pytest.mark.parametrize(
    "instance",
    reference.MALFORMED_GRAPHS + [{"n": 3, "edges": [], "k": 1}],  # extra key
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        ThreeColoring.validate(instance)


def test_size():
    assert ThreeColoring.size({"n": 4, "edges": K4}) == 10
