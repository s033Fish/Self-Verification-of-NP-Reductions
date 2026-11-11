"""Tests for Vertex Cover. Run with: uv run pytest"""

from __future__ import annotations

import random

import pytest
import reference

from benchmark.problems import InvalidInstance, VertexCover, check_problem

TRIANGLE = [[0, 1], [1, 2], [0, 2]]
STAR = [[0, 1], [0, 2], [0, 3]]


def test_interface():
    counts = check_problem(VertexCover)
    assert counts["enumerated"] == 6505


@pytest.mark.parametrize(
    "n, edges, k, expected",
    [
        (3, TRIANGLE, 2, True),
        (3, TRIANGLE, 1, False),
        (4, STAR, 1, True),               # the centre covers every edge
        (3, [], 0, True),                 # nothing to cover
        (0, [], 0, True),
        (3, TRIANGLE, -1, False),         # k < 0
        (3, TRIANGLE, 5, True),           # k >= n
    ],
)
def test_hand_checked(n, edges, k, expected):
    instance = {"n": n, "edges": edges, "k": k}
    VertexCover.validate(instance)
    assert VertexCover.is_yes(instance) is expected


def test_matches_reference_on_enumeration():
    for instance in VertexCover.enumerate_instances(VertexCover.exhaustive_scale):
        assert VertexCover.is_yes(instance) == reference.vertex_cover(**instance)


def test_matches_reference_on_random_instances():
    rng = random.Random(0)
    for _ in range(300):
        instance = VertexCover.random_instance(rng, rng.randint(5, 10))
        assert VertexCover.is_yes(instance) == reference.vertex_cover(**instance)


@pytest.mark.parametrize(
    "instance",
    [reference.with_k(g) for g in reference.MALFORMED_GRAPHS]
    + [
        {"n": 3, "edges": []},
        {"n": 3, "edges": [], "k": True},
        {"n": 3, "edges": [], "k": 1.0},       # float k
    ],
)
def test_malformed_instances_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        VertexCover.validate(instance)


def test_size():
    assert VertexCover.size({"n": 4, "edges": STAR, "k": 1}) == 7
