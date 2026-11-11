"""Independent Set."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem
from .graph_common import (
    adjacency,
    enumerate_graphs_with_k,
    graph_size,
    max_independent_set_size,
    random_graph_with_k,
    validate_graph_with_k,
)


class IndependentSet(Problem):
    """Independent Set.

    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
      * Vertices are 0..n-1. Edges are undirected pairs [u, v] with u != v;
        [u, v] and [v, u] are the same edge and may not both appear.
      * k is any integer.

    Yes iff the graph has an independent set of AT LEAST k vertices: k
    vertices with no edge between any two of them.

    Edge cases: k <= 0 is always yes. k > n is always no. With no edges,
    every set of vertices is independent.
    """

    name = "Independent Set"
    exhaustive_scale = 5

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_graph_with_k(instance)

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        n, k = instance["n"], instance["k"]
        if k <= 0:
            return True
        if k > n:
            return False
        return max_independent_set_size(n, adjacency(n, instance["edges"])) >= k

    @classmethod
    def size(cls, instance: Instance) -> int:
        return graph_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        return random_graph_with_k(rng, scale)

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        return enumerate_graphs_with_k(scale)
