"""Tests for the problem interface and shared helpers.

Run with: uv run pytest
"""

from __future__ import annotations

import random

import pytest

from benchmark.problems.base import (
    InvalidInstance,
    Problem,
    all_graphs,
    canonical,
    check_problem,
    random_graph,
    require_int,
    require_keys,
    validate_cnf,
    validate_graph,
)


class HasEdge(Problem):
    """Instance: {"n": int, "edges": [[u, v], ...]}. Yes iff there is at least one edge."""

    name = "Has Edge"
    exhaustive_scale = 4

    @classmethod
    def validate(cls, instance):
        require_keys(instance, {"n", "edges"})
        validate_graph(instance)

    @classmethod
    def is_yes(cls, instance):
        return bool(instance["edges"])

    @classmethod
    def size(cls, instance):
        return instance["n"] + len(instance["edges"])

    @classmethod
    def random_instance(cls, rng, scale):
        return {"n": scale, "edges": random_graph(rng, scale)}

    @classmethod
    def enumerate_instances(cls, scale):
        for n in range(scale + 1):
            for edges in all_graphs(n):
                yield {"n": n, "edges": edges}


def test_conforming_problem_passes():
    counts = check_problem(HasEdge)
    # Graphs on 0..4 vertices: 1 + 1 + 2 + 8 + 64.
    assert counts["enumerated"] == 76
    assert counts["yes"] + counts["no"] == 76


def test_incomplete_problem_is_rejected_at_definition():
    with pytest.raises(TypeError, match="must implement"):

        class Incomplete(Problem):  # noqa: F841
            """Missing every method."""

            name = "Incomplete"
            exhaustive_scale = 1


def test_problem_without_docstring_is_rejected():
    with pytest.raises(TypeError, match="docstring"):

        class Undocumented(HasEdge):  # noqa: F841
            __doc__ = None


def test_problems_are_not_instantiated():
    with pytest.raises(TypeError):
        HasEdge()


def test_graph_count_matches_formula():
    assert sum(1 for _ in all_graphs(5)) == 2**10


@pytest.mark.parametrize(
    "instance",
    [
        {"n": 3, "edges": [[0, 3]]},          # vertex out of range
        {"n": 3, "edges": [[1, 1]]},          # self-loop
        {"n": 3, "edges": [[0, 1], [1, 0]]},  # duplicate edge
        {"n": 3, "edges": [[0, "1"]]},        # non-int endpoint
        {"n": 3, "edges": [[0, 1, 2]]},       # not a pair
        {"n": True, "edges": []},             # bool is not an int
        {"n": -1, "edges": []},               # negative n
    ],
)
def test_malformed_graphs_are_rejected(instance):
    with pytest.raises(InvalidInstance):
        validate_graph(instance)


def test_wrong_keys_are_rejected():
    with pytest.raises(InvalidInstance):
        require_keys({"n": 2, "edges": [], "k": 1}, {"n", "edges"})
    with pytest.raises(InvalidInstance):
        require_keys([1, 2], {"n", "edges"})


def test_cnf_validation():
    validate_cnf([[1, -2], [], [3]], 3)
    for clauses, num_vars in ([[0]], 2), ([[3]], 2), ([["1"]], 2), ([1, 2], 2):
        with pytest.raises(InvalidInstance):
            validate_cnf(clauses, num_vars)


def test_require_int_minimum():
    require_int(0, "k", minimum=0)
    with pytest.raises(InvalidInstance):
        require_int(-1, "k", minimum=0)


def test_random_graph_is_valid_and_repeatable():
    first = random_graph(random.Random(7), 6)
    second = random_graph(random.Random(7), 6)
    assert first == second
    validate_graph({"n": 6, "edges": first})


def test_canonical_ignores_key_order():
    assert canonical({"n": 1, "edges": []}) == canonical({"edges": [], "n": 1})
