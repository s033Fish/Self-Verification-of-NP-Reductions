"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) asks whether an undirected graph
contains a cycle that visits every vertex exactly once.
The target problem (HamiltonianPath) asks whether an undirected graph
contains a *path* (not necessarily a cycle) that visits every vertex
exactly once.

We implement the classic polynomial‑time reduction:

* Choose an arbitrary vertex `v` of the input graph `G` (we use the last
  vertex `v = n-1`).
* Remove `v` from the graph.
* Introduce two new vertices `s` and `t`.
* Connect `s` and `t` to **all** former neighbours of `v`.

The resulting graph `G'` has `n+1` vertices.  There is a Hamiltonian path
from `s` to `t` in `G'` iff there is a Hamiltonian cycle in `G`:

* If `G` has a Hamiltonian cycle, delete the edges incident to `v`. The
  remaining edges form a Hamiltonian *path* between the two neighbours of
  `v` on the cycle.  Adding `s` adjacent to the first neighbour and `t`
  adjacent to the second neighbour yields a Hamiltonian `s‑t` path in `G'`.
* Conversely, a Hamiltonian `s‑t` path in `G'` must start at `s`, go to a
  neighbour `a` of `v`, traverse a Hamiltonian path of the original graph
  (without `v`) ending at another neighbour `b` of `v`, and finally go to
  `t`.  Adding the vertex `v` with edges `(v,a)` and `(v,b)` (which exist in
  the original graph) closes the cycle.

Edge cases where the source instance is a trivial “no” (graphs with
`n <= 2`) are mapped to a target instance that is also a trivial “no"
(`n = 0`).  This preserves correctness while keeping the implementation
simple.

The function runs in time linear in the size of the input graph, which
is polynomial.
"""

from __future__ import annotations
from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": [[u, v], ...]}`` describing an undirected
        simple graph as defined in ``problems.py`` for the source problem.

    Returns
    -------
    dict
        An instance of the target problem (HamiltonianPath) with the same
        format.  The answer to the returned instance is *yes* exactly when
        the answer to the input instance is *yes*.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial cases: source is always NO for n <= 2.  Return a target
    # instance that is also a definite NO (n = 0, no edges).
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose the vertex to remove: the last vertex (n-1).
    v = n - 1

    # Collect neighbours of v and edges that do NOT involve v.
    neighbours = set()
    new_edges: List[List[int]] = []
    for u, w in edges:
        if u == v or w == v:
            # Edge incident to the removed vertex.
            other = w if u == v else u
            neighbours.add(other)
        else:
            new_edges.append([u, w])

    # Indices for the two new vertices.
    s = n - 1  # reuse the index formerly occupied by v
    t = n      # new index after the original vertices 0..n-2

    # Connect s and t to every former neighbour of v.
    for u in neighbours:
        new_edges.append([u, s])
        new_edges.append([u, t])

    # The new graph has (n-1) original vertices + 2 new vertices = n+1.
    return {"n": n + 1, "edges": new_edges}

