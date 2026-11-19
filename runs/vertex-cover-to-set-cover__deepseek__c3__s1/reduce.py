"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Construction: the universe has one element per edge of the graph, and for
every vertex v there is a set containing exactly the edges incident to v.
A vertex cover C of size t makes the sets {S_v : v in C} cover every edge
(each edge has an endpoint in C), so the set cover has size <= t.
Conversely, any collection of t sets that covers the universe is a set of
t vertices whose union is a vertex cover (every edge is incident to one of
the chosen vertices), so the vertex cover has size <= t.  Hence the two
optima are equal and the "at most k" answers coincide.

Edge cases:
  * k < 0: both problems answer no.
  * no edges: universe_size = 0, which Set Cover answers yes for every k >= 0.
  * k >= n: all n sets cover the universe, so the answer is yes.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to a Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element per edge.
    universe_size = len(edges)

    # S_v = set of edge indices incident to vertex v.
    sets: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": universe_size, "sets": sets, "k": k}
