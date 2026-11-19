"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G = (V, E) we construct a new graph G' = (V', E')
as follows:

* If |V| = 0, we output the empty graph (no vertices).  The original
  instance is a NO‑instance and the empty graph has no Hamiltonian cycle.

* If |V| = 1, the original instance is always a YES‑instance (a single
  vertex trivially forms a Hamiltonian path).  We therefore output a fixed
  triangle (three vertices fully connected) which always has a Hamiltonian
  cycle.

* For |V| >= 2 we add a new vertex *s* and connect it to every vertex of
  the original graph.  Formally, V' = V ∪ {s} where s = |V| and
  E' = E ∪ {{s, v} : v ∈ V}.  It is well‑known that G has a Hamiltonian
  path iff G' has a Hamiltonian cycle: a Hamiltonian cycle in G' must visit
  *s* exactly once; removing *s* yields a Hamiltonian path in G, and any
  Hamiltonian path in G can be closed into a cycle by inserting *s* between
  its two endpoints.

The construction runs in polynomial time and the produced instance obeys
the validation rules of :class:`HamiltonianCycle`.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianPath, HamiltonianCycle


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dict representing a Hamiltonian‑Path instance.  It must pass
        ``HamiltonianPath.validate``.

    Returns
    -------
    dict
        A dict representing a Hamiltonian‑Cycle instance.  The returned
        instance is guaranteed to be valid according to
        ``HamiltonianCycle.validate``.
    """
    # Validate the source instance first – this will raise InvalidInstance
    # if the format is wrong.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = list(instance["edges"])  # shallow copy

    # Case n == 0: output empty graph – no Hamiltonian cycle.
    if n == 0:
        return {"n": 0, "edges": []}

    # Case n == 1: always YES for path, so output a guaranteed YES‑instance
    # for cycle (a triangle).
    if n == 1:
        triangle_edges = [[0, 1], [1, 2], [2, 0]]
        return {"n": 3, "edges": triangle_edges}

    # General case: add a new vertex ``s`` = n and connect it to all
    # original vertices.
    new_n = n + 1
    # Add edges from the new vertex to each existing vertex.
    new_edges = edges + [[n, v] for v in range(n)]
    # Return the constructed instance.
    result = {"n": new_n, "edges": new_edges}
    # Validate the target instance before returning (helps catch bugs).
    HamiltonianCycle.validate(result)
    return result
