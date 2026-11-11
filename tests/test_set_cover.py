"""Tests for Set Cover. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import InvalidInstance, SetCover, check_problem


def test_interface():
    counts = check_problem(SetCover)
    assert counts["yes"] and counts["no"]


@pytest.mark.parametrize(
    "universe_size, sets, k, expected",
    [
        (3, [[0, 1], [1, 2], [2]], 1, False),
        (3, [[0, 1], [1, 2], [2]], 2, True),
        (3, [[0, 1], [1]], 5, False),             # element 2 is in no set
        (0, [], 0, True),                         # empty universe
        (2, [[0, 1]], -1, False),                 # k < 0
        (2, [[0, 1], [0, 1]], 1, True),           # duplicate sets are fine
        (2, [[], [1, 0]], 1, True),               # empty set, unsorted set
    ],
)
def test_hand_checked(universe_size, sets, k, expected):
    instance = {"universe_size": universe_size, "sets": sets, "k": k}
    SetCover.validate(instance)
    assert SetCover.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in SetCover.enumerate_instances(SetCover.exhaustive_scale):
        assert SetCover.is_yes(instance) == reference.set_cover(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = SetCover.random_instance(rng, rng.randint(3, 7))
        assert SetCover.is_yes(instance) == reference.set_cover(**instance)


@pytest.mark.parametrize(
    "instance",
    [
        {"universe_size": 2, "sets": [[2]], "k": 1},          # element out of range
        {"universe_size": 2, "sets": [[0, 0]], "k": 1},       # repeated element
        {"universe_size": 2, "sets": [[True]], "k": 1},       # bool element
        {"universe_size": -1, "sets": [], "k": 1},            # negative universe
        {"universe_size": 2, "sets": [0, 1], "k": 1},         # sets not lists
        {"universe_size": 2, "sets": [[0]]},                  # missing k
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        SetCover.validate(instance)


def test_size():
    # universe 3 + 2 sets + 3 element entries
    assert SetCover.size({"universe_size": 3, "sets": [[0, 1], [2]], "k": 2}) == 8
