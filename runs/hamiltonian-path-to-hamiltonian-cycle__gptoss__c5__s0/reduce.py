"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The reduction works as follows:

* For a graph G = (V, E) with |V| = n we construct a new graph G' = (V', E')
  where V' = V ∪ {s} and s is a new vertex.
* E' contains all original edges E and additionally connects s to **every**
  vertex in V.

For n ≥ 2 this classic construction has the property that G has a Hamiltonian
path iff G' has a Hamiltonian cycle: any Hamiltonian cycle in G' must use the
new vertex s exactly once, and removing s from that cycle yields a Hamiltonian
path in G. Conversely, a Hamiltonian path in G can be closed into a cycle by
adding the edges to s.

The construction does not work for the trivial cases n = 0, 1.  Those are
handled explicitly so that the reduction preserves the answer:

* n = 0 : the input instance is a "no" instance.  We output the empty graph
  (n = 0) which is also a "no" instance for Hamiltonian Cycle.
* n = 1 : the input instance is a "yes" instance (the single vertex).  We output
  a triangle (three vertices forming a cycle) which is a "yes" instance for
  Hamiltonian Cycle.
* n = 2 : the generic construction works, because the resulting graph has three
  vertices.  The cycle exists exactly when the original edge (0, 1) is present.

The function ``reduce`` validates the source instance using the provided
``HamiltonianPath.validate`` method and returns a new instance that conforms
to ``HamiltonianCycle``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianPath, HamiltonianCycle

def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` describing an undirected
        graph, conforming to :class:`HamiltonianPath`.

    Returns
    -------
    dict
        A dictionary suitable for :class:`HamiltonianCycle`.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case handling ----------------------------------------------------
    if n == 0:
        # Empty graph – no Hamiltonian cycle.
        return {"n": 0, "edges": []}
    if n == 1:
        # Single vertex path is yes. Return a triangle (3‑cycle).
        # Vertices: 0, 1, 2. All three edges present.
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General case (n >= 2) -----------------------------------------------
    # New vertex index
    s = n
    new_n = n + 1
    # Start with a copy of the original edges.
    new_edges: List[List[int]] = [edge[:] for edge in edges]
    # Connect the new vertex to every original vertex.
    for v in range(n):
        new_edges.append([s, v])

    # Return the constructed instance.
    return {"n": new_n, "edges": new_edges}

