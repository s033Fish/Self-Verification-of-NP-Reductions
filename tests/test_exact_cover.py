"""Tests for Exact Cover. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import ExactCover, InvalidInstance, check_problem


def test_interface():
    counts = check_problem(ExactCover)
    assert counts["enumerated"] == 2 + 4 + 16 + 256  # universes of size 0..3


@pytest.mark.parametrize(
    "universe_size, sets, expected",
    [
        (3, [[0, 1], [1, 2], [2]], True),         # {0,1} + {2}
        (3, [[0, 1], [1, 2]], False),             # overlap on 1
        (0, [], True),                            # empty universe
        (1, [[]], False),                         # empty set covers nothing
        (2, [[0, 1], [0, 1]], True),              # either copy alone
        (4, [[0, 1], [1, 2], [2, 3]], True),      # {0,1} + {2,3}
        (4, [[0, 1], [1, 2], [2]], False),        # element 3 never covered
    ],
)
def test_hand_checked(universe_size, sets, expected):
    instance = {"universe_size": universe_size, "sets": sets}
    ExactCover.validate(instance)
    assert ExactCover.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in ExactCover.enumerate_instances(ExactCover.exhaustive_scale):
        assert ExactCover.is_yes(instance) == reference.exact_cover(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = ExactCover.random_instance(rng, rng.randint(3, 6))
        assert ExactCover.is_yes(instance) == reference.exact_cover(**instance)


@pytest.mark.parametrize(
    "instance",
    [
        {"universe_size": 2, "sets": [[2]]},
        {"universe_size": 2, "sets": [[1, 1]]},
        {"universe_size": 2, "sets": [["0"]]},
        {"universe_size": 2, "sets": [[0]], "k": 1},          # extra key
        {"sets": [[0]]},                                      # missing key
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        ExactCover.validate(instance)


def test_size():
    assert ExactCover.size({"universe_size": 3, "sets": [[0, 1], [2]]}) == 8
