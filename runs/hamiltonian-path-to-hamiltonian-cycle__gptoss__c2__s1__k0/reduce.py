"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem (HamiltonianPath) asks whether an undirected graph
contains a path that visits every vertex exactly once.  The target problem
(HamiltonianCycle) asks whether there is a cycle that visits every vertex
exactly once and returns to its start.

Standard polynomial‑time reduction:
    * Given a graph G = (V, E) with |V| = n, create a new vertex s and
      connect it to every vertex of V.  Let G' be the resulting graph on
      n+1 vertices.
    * G has a Hamiltonian path iff G' has a Hamiltonian cycle.

Edge‑case handling:
    * n = 0 – the source instance is a "no" instance.  G' will have a
      single vertex (n = 1) and by the definition of HamiltonianCycle the
      answer is also "no".
    * n = 1 – the source instance is always a "yes" instance (the single
      vertex itself is a Hamiltonian path).  Adding a universal vertex would
      produce a graph with n = 2, which is always a "no" instance for the
      target.  To preserve correctness we instead output a fixed triangle
      (three vertices forming a cycle), which is a guaranteed "yes"
      instance.
    * n = 2 – the standard construction works: the added vertex creates a
      triangle exactly when the original edge exists, matching the source
      answer.

The function ``reduce`` implements this transformation.  It runs in O(n+|E|)
time, i.e., polynomial in the size of the input.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists) representing an undirected graph as specified in
        ``problems.py`` for ``HamiltonianPath``.

    Returns
    -------
    dict
        An instance suitable for ``HamiltonianCycle`` with the property
        that the answer is "yes" exactly when the original instance's answer
        is "yes".
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Special handling for n == 1 (source is always yes).
    if n == 1:
        # Return a simple triangle which is a guaranteed yes‑instance for
        # HamiltonianCycle.
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General case: add a new universal vertex numbered n.
    new_n = n + 1
    new_edges = list(edges)  # shallow copy of original edges
    # Connect the new vertex to every original vertex.
    universal_edges = [[n, v] for v in range(n)]
    new_edges.extend(universal_edges)

    return {"n": new_n, "edges": new_edges}

