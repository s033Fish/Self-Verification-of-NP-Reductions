"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Standard construction: given G = (V, E) with V = {0, ..., n-1}, build G' by
adding one new vertex x = n adjacent to every vertex of G.  Then G has a
Hamiltonian path iff G' has a Hamiltonian cycle:

  * (=>) a Hamiltonian path v_0, ..., v_{n-1} of G yields the cycle
    x, v_0, ..., v_{n-1}, x in G'.
  * (<=) a Hamiltonian cycle of G' must use exactly two edges incident to x,
    say x-u and x-v; removing x leaves a Hamiltonian path of G from u to v.

The construction is only valid for n >= 2 (for n = 1 the new graph has two
vertices and can never contain a cycle, while the source instance is a yes).
The tiny cases are handled explicitly:

  * n = 0 : source is no  -> return the empty graph (target is no).
  * n = 1 : source is yes -> return the triangle (target is yes).
  * n >= 2: apply the construction above.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no Hamiltonian path; emit a graph with no Hamiltonian cycle.
    if n == 0:
        return {"n": 0, "edges": []}

    # n = 1: the single vertex is a Hamiltonian path; emit the triangle,
    # which is the smallest graph with a Hamiltonian cycle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add new vertex n adjacent to every original vertex.
    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([v, n])
    return {"n": n + 1, "edges": new_edges}
