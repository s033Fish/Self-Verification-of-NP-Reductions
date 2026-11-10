"""Problem definitions for this task.

Instances are plain dicts, so they can be written to and read from JSON.
Vertices are numbered 0..n-1 and edges are undirected pairs [u, v] with u != v.
Each problem has a brute-force `is_yes(instance)` solver for small instances
and a `random_instance(rng, n)` generator for testing.
"""

from __future__ import annotations

import random
from itertools import combinations


def _random_graph(rng: random.Random, n: int, p: float) -> list[list[int]]:
    return [[u, v] for u, v in combinations(range(n), 2) if rng.random() < p]


class IndependentSet:
    """Instance: {"n": int, "edges": [[u, v], ...], "k": int}.

    Yes iff some set of k vertices has no edge between any two of them.
    """

    @staticmethod
    def is_yes(instance: dict) -> bool:
        n, k = instance["n"], instance["k"]
        if k <= 0:
            return True
        if k > n:
            return False
        edges = {frozenset(edge) for edge in instance["edges"]}
        return any(
            all(frozenset(pair) not in edges for pair in combinations(subset, 2))
            for subset in combinations(range(n), k)
        )

    @staticmethod
    def random_instance(rng: random.Random, n: int) -> dict:
        return {"n": n, "edges": _random_graph(rng, n, rng.random()), "k": rng.randint(0, n)}


class VertexCover:
    """Instance: {"n": int, "edges": [[u, v], ...], "k": int}.

    Yes iff some set of at most k vertices touches every edge.
    """

    @staticmethod
    def is_yes(instance: dict) -> bool:
        n, k = instance["n"], instance["k"]
        if k < 0:
            return False
        edges = [tuple(edge) for edge in instance["edges"]]
        for size in range(min(k, n) + 1):
            for subset in combinations(range(n), size):
                chosen = set(subset)
                if all(u in chosen or v in chosen for u, v in edges):
                    return True
        return False

    @staticmethod
    def random_instance(rng: random.Random, n: int) -> dict:
        return {"n": n, "edges": _random_graph(rng, n, rng.random()), "k": rng.randint(0, n)}


SOURCE = IndependentSet
TARGET = VertexCover
