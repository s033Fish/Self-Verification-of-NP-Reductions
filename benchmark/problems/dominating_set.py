"""Dominating Set."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem
from .graph_common import (
    adjacency,
    enumerate_graphs_with_k,
    graph_size,
    min_dominating_set_size,
    random_graph_with_k,
    validate_graph_with_k,
)


class DominatingSet(Problem):
    """Dominating Set.

    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
      * Vertices are 0..n-1. Edges are undirected pairs [u, v] with u != v;
        [u, v] and [v, u] are the same edge and may not both appear.
      * k is any integer.

    Yes iff the graph has a dominating set of AT MOST k vertices: a set D
    such that every vertex is in D or adjacent to a vertex in D.

    Edge cases: k < 0 is always no. n = 0 is yes for every k >= 0. k >= n
    is yes. An isolated vertex must itself be in D.
    """

    name = "Dominating Set"
    exhaustive_scale = 5

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_graph_with_k(instance)

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        n, k = instance["n"], instance["k"]
        if k < 0:
            return False
        if k >= n:
            return True
        return min_dominating_set_size(n, adjacency(n, instance["edges"])) <= k

    @classmethod
    def size(cls, instance: Instance) -> int:
        return graph_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        return random_graph_with_k(rng, scale)

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        return enumerate_graphs_with_k(scale)
