"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

We use the classic reduction that removes a distinguished vertex (chosen as 0)
and replaces it by two new vertices ``s`` and ``t``.  ``s`` and ``t`` are each
connected to every former neighbor of ``0``.  All other edges of the original
graph are kept, but edges incident to ``0`` are omitted.

* If the original graph has a Hamiltonian **cycle**, delete vertex ``0`` and
  break the cycle at the two edges incident to ``0``.  The remaining vertices
  form a Hamiltonian **path** whose endpoints are exactly the two former
  neighbors of ``0``.  Replacing those endpoints by ``s`` and ``t`` yields a
  Hamiltonian path in the constructed graph.
* Conversely, any Hamiltonian path in the constructed graph must start at ``s``
  and end at ``t`` (they are the only vertices of degree equal to the number of
  original neighbors of ``0``; all other vertices have degree at least two in a
  Hamiltonian path).  Removing ``s`` and ``t`` and re‑inserting vertex ``0``
  together with its two incident edges restores a Hamiltonian cycle in the
  original graph.

For graphs with ``n <= 2`` the source instance is defined to be a NO‑instance.
We map those to a trivially NO Hamiltonian‑Path instance (``n = 0`` with no
edges).  The construction runs in O(n + |E|) time, i.e. polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Set

from problems import HamiltonianCycle, HamiltonianPath


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance:
        Graph instance for :class:`HamiltonianCycle`.

    Returns
    -------
    dict
        Graph instance for :class:`HamiltonianPath` with the same answer.
    """

    # Validate source instance.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial NO cases (n <= 2).
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the distinguished vertex.
    # Compute its neighbor set.
    neighbor_set: Set[int] = set()
    remaining_edges: List[List[int]] = []
    for u, v in edges:
        if u == 0:
            neighbor_set.add(v)
        elif v == 0:
            neighbor_set.add(u)
        else:
            remaining_edges.append([u, v])

    # New vertices s and t.
    s = n          # index for s
    t = n + 1      # index for t
    new_n = n + 2

    new_edges: List[List[int]] = []
    # Keep edges not incident to 0.
    new_edges.extend(remaining_edges)
    # Connect s and t to each former neighbor of 0.
    for v in neighbor_set:
        new_edges.append([s, v])
        new_edges.append([t, v])
    # No edge between s and t.

    reduced_instance = {"n": new_n, "edges": new_edges}
    # Validate the target instance.
    HamiltonianPath.validate(reduced_instance)
    return reduced_instance

