"""Polynomial-time reduction from Vertex Cover to Set Cover.

Reduction
---------
Given a Vertex Cover instance ``{"n": n, "edges": edges, "k": k}``:

  * The universe of the Set Cover instance is the set of *edge indices*
    0 .. m-1, where ``m = len(edges)``.  Covering the whole universe means
    every edge is "hit".
  * For each vertex ``v`` in ``0 .. n-1`` we create one set containing the
    indices of all edges incident to ``v``.
  * The budget ``k`` is copied unchanged.

A subset ``S`` of vertices covers every edge iff the corresponding family
of sets covers every edge index.  Hence the graph has a vertex cover of
size at most ``k`` iff the set system has a set cover of size at most
``k``.

Edge cases line up exactly:
  * ``k < 0``: both answers are no.
  * no edges (``m == 0``): the universe is empty, so the target is yes for
    every ``k >= 0``, matching the source.
  * ``k >= n``: the ``n`` sets cover the whole universe, so the target is
    yes, matching the source.

The construction runs in time O(n * m) (polynomial) and never calls a
solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    m = len(edges)

    # sets[v] = indices of edges incident to vertex v
    sets: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": m, "sets": sets, "k": k}
