"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem (HamiltonianPath) asks whether an undirected graph
has a path that visits every vertex exactly once.  The target problem
(HamiltonianCycle) asks for a Hamiltonian *cycle*.

Standard textbook reduction: given a graph G = (V, E) with |V| = n, add a
new vertex ``v_new`` and connect it to every vertex of G.  The resulting
graph G' = (V ∪ {v_new}, E ∪ {{v_new, u} : u ∈ V}) has a Hamiltonian
cycle iff G has a Hamiltonian path – simply delete ``v_new`` from a
Hamiltonian cycle of G' to obtain a Hamiltonian path of G, and conversely
add ``v_new`` between the two endpoints of a Hamiltonian path of G.

The reduction must also handle the small edge‑case inputs where the
source and target definitions differ (e.g., n = 0, 1, 2).  The mapping
chosen below preserves the answer for all possible inputs while keeping
the construction polynomial.

Implementation details
----------------------
* The function ``reduce(instance)`` receives a dictionary matching the
  source format: ``{"n": int, "edges": [[u, v], ...]}``.
* It returns a dictionary in the target format with the same keys.
* All edges are stored as unordered pairs ``[u, v]`` with ``u != v``.
* No duplicate edges are introduced.

The cases are:

* **n = 0** – source answer is *no*.  We return the empty graph (n = 0),
  which is also a *no* instance for Hamiltonian Cycle.
* **n = 1** – source answer is *yes*.  We return a triangle (3 vertices,
  all three edges) which trivially has a Hamiltonian cycle.
* **n = 2** – source answer is *yes* iff the single possible edge ``[0,1]``
  exists.  We construct a 3‑vertex graph consisting of the two original
  vertices plus a new vertex ``2`` connected to both.  A Hamiltonian cycle
  exists exactly when the edge ``[0,1]`` is also present, matching the
  source condition.
* **n ≥ 3** – apply the standard reduction by adding a new vertex ``n``
  and connecting it to every original vertex.

The construction runs in O(n + |E|) time, which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _edge_key(edge: List[int]) -> tuple[int, int]:
    """Return a canonical (sorted) tuple representation of an undirected edge.

    This helper is used to detect the presence of an edge regardless of the
    order of its endpoints.
    """
    u, v = edge
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of unordered vertex pairs) describing an undirected graph.

    Returns
    -------
    dict
        An instance of the Hamiltonian‑Cycle problem that is a *yes* instance
        exactly when the input instance is a *yes* instance.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Helper: build a set of canonical edge tuples for fast lookup.
    edge_set = {_edge_key(e) for e in edges}

    # Case n = 0: both problems are a definite "no".
    if n == 0:
        return {"n": 0, "edges": []}

    # Case n = 1: source is always yes. Return a triangle which has a Hamiltonian cycle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # Case n = 2: source is yes iff edge (0,1) exists.
    if n == 2:
        # New vertex will be index 2.
        new_edges: List[List[int]] = [[0, 2], [1, 2]]
        if (0, 1) in edge_set:
            new_edges.append([0, 1])
        return {"n": 3, "edges": new_edges}

    # General case n >= 3: add a new vertex n and connect it to every original vertex.
    new_n = n + 1
    new_edges = [list(e) for e in edges]  # copy original edges
    # Connect new vertex to all existing vertices.
    new_edges.extend([[i, n] for i in range(n)])
    return {"n": new_n, "edges": new_edges}


__all__ = ["reduce"]
