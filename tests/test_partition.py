"""Tests for Partition. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import InvalidInstance, Partition, check_problem


def test_interface():
    counts = check_problem(Partition)
    assert counts["enumerated"] == 1 + 4 + 16 + 64 + 256  # lengths 0..4, values 0..3


@pytest.mark.parametrize(
    "numbers, expected",
    [
        ([1, 5, 11, 5], True),                    # {11} vs {1, 5, 5}
        ([1, 2, 5], False),
        ([], True),
        ([3], False),
        ([0, 0], True),
        ([1, 1], True),
        ([2, 3, 5], True),                        # {5} vs {2, 3}
    ],
)
def test_hand_checked(numbers, expected):
    instance = {"numbers": numbers}
    Partition.validate(instance)
    assert Partition.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in Partition.enumerate_instances(Partition.exhaustive_scale):
        assert Partition.is_yes(instance) == reference.partition(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = Partition.random_instance(rng, rng.randint(2, 12))
        assert Partition.is_yes(instance) == reference.partition(**instance)


@pytest.mark.parametrize(
    "instance",
    [
        {"numbers": [-2, 2]},
        {"numbers": [False]},
        {"numbers": [1], "target": 1},            # extra key
        {"values": [1]},                          # wrong key
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        Partition.validate(instance)


def test_size():
    assert Partition.size({"numbers": [1, 2, 3]}) == 3 + 1 + 2 + 2
