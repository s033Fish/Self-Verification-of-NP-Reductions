"""3-Coloring."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem
from .graph_common import (
    adjacency,
    enumerate_graphs,
    graph_size,
    random_plain_graph,
    three_colourable,
    validate_plain_graph,
)


class ThreeColoring(Problem):
    """3-Coloring (graph 3-colorability).

    Instance: {"n": n, "edges": [[u, v], ...]}
      * Vertices are 0..n-1. Edges are undirected pairs [u, v] with u != v;
        [u, v] and [v, u] are the same edge and may not both appear.

    Yes iff each vertex can be given one of 3 colours so that the two
    endpoints of every edge get different colours. Not every colour has to
    be used.

    Edge cases: n = 0 is yes. Any graph with at most 3 vertices is yes. A
    graph containing 4 mutually adjacent vertices (K4) is no.
    """

    name = "3-Coloring"
    exhaustive_scale = 5

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_plain_graph(instance)

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        n = instance["n"]
        return three_colourable(n, adjacency(n, instance["edges"]))

    @classmethod
    def size(cls, instance: Instance) -> int:
        return graph_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        return random_plain_graph(rng, scale)

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        return enumerate_graphs(scale)
