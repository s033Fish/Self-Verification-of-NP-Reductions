"""Hamiltonian Cycle."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem
from .graph_common import (
    adjacency,
    enumerate_graphs,
    graph_size,
    hamiltonian_cycle_exists,
    random_plain_graph,
    validate_plain_graph,
)


class HamiltonianCycle(Problem):
    """Hamiltonian Cycle (undirected).

    Instance: {"n": n, "edges": [[u, v], ...]}
      * Vertices are 0..n-1. Edges are undirected pairs [u, v] with u != v;
        [u, v] and [v, u] are the same edge and may not both appear.

    Yes iff there is a cycle that visits every vertex exactly once and
    returns to its start, using only edges of the graph.

    Edge cases: graphs with n <= 2 are always no (a simple graph needs at
    least 3 vertices to have a cycle), including n = 0. n = 3 is yes only
    for the triangle.
    """

    name = "Hamiltonian Cycle"
    # Solver is O(2^n * n^2): fine to about 20 vertices, slow beyond.
    exhaustive_scale = 5

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_plain_graph(instance)

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        n = instance["n"]
        return hamiltonian_cycle_exists(n, adjacency(n, instance["edges"]))

    @classmethod
    def size(cls, instance: Instance) -> int:
        return graph_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        return random_plain_graph(rng, scale)

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        return enumerate_graphs(scale)
