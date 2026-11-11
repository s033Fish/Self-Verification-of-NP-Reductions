"""Tests for Subset Sum. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import InvalidInstance, SubsetSum, check_problem


def test_interface():
    counts = check_problem(SubsetSum)
    assert counts["yes"] and counts["no"]


@pytest.mark.parametrize(
    "numbers, target, expected",
    [
        ([3, 5, 7], 12, True),
        ([3, 5, 7], 11, False),
        ([3, 5, 7], 0, True),                     # empty sub-list
        ([3, 5, 7], -1, False),
        ([], 0, True),
        ([], 1, False),
        ([2, 2], 4, True),                        # repeated values
        ([10**30, 1], 10**30 + 1, True),          # very large numbers
    ],
)
def test_hand_checked(numbers, target, expected):
    instance = {"numbers": numbers, "target": target}
    SubsetSum.validate(instance)
    assert SubsetSum.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in SubsetSum.enumerate_instances(SubsetSum.exhaustive_scale):
        assert SubsetSum.is_yes(instance) == reference.subset_sum(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = SubsetSum.random_instance(rng, rng.randint(3, 12))
        assert SubsetSum.is_yes(instance) == reference.subset_sum(**instance)


@pytest.mark.parametrize(
    "instance",
    [
        {"numbers": [-1, 2], "target": 1},        # negative number
        {"numbers": [True], "target": 1},         # bool number
        {"numbers": [1.5], "target": 1},          # float number
        {"numbers": [1], "target": "1"},          # string target
        {"numbers": [1]},                         # missing target
        {"numbers": 5, "target": 5},              # numbers not a list
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        SubsetSum.validate(instance)


def test_size():
    # 2 numbers + bits(5)=3 + bits(8)=4 + bits(13)=4
    assert SubsetSum.size({"numbers": [5, 8], "target": 13}) == 13
