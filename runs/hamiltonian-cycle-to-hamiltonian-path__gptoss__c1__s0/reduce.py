"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) expects an undirected graph given as
``{"n": n, "edges": [[u, v], ...]}`` where vertices are numbered 0..n-1.
The target problem (HamiltonianPath) uses the same representation.

We implement the classic polynomial‑time reduction:

* For graphs with n <= 2 the source instance is always a *no* instance (by the
  definition of Hamiltonian Cycle).  For such cases we return a trivially
  *no* Hamiltonian‑Path instance – an empty graph with n = 0.  This keeps the
  answer consistent.
* For larger graphs we add a fresh vertex ``s`` (number ``n``) and connect it
  to **every** original vertex.  The resulting graph has ``n+1`` vertices.
  The following claim holds:

  *If the original graph has a Hamiltonian cycle, then the augmented graph has
  a Hamiltonian path (starting at the new vertex ``s`` and then following the
  cycle, stopping before returning to the start).*

  Conversely, any Hamiltonian path in the augmented graph must start at the
  new vertex (otherwise ``s`` would be an interior vertex, forcing a repeat of
  some original vertex).  Removing ``s`` from such a path yields a Hamiltonian
  cycle in the original graph.

  Hence the answer to the target instance is *yes* exactly when the answer to
  the source instance is *yes*.

The reduction runs in O(n + |E|) time, which is polynomial.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance: dict
        ``{"n": n, "edges": [[u, v], ...]}`` describing an undirected graph.

    Returns
    -------
    dict
        An instance of the Hamiltonian‑Path problem with the property that
        it is a *yes* instance iff the input instance is a *yes* instance.
    """

    n = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge cases where the source is always a NO instance.
    if n <= 2:
        # Return a trivially NO Hamiltonian‑Path instance: empty graph.
        return {"n": 0, "edges": []}

    # Build the new edge list: copy original edges and add edges from the new
    # vertex (labelled n) to every original vertex 0..n-1.
    new_edges = [list(e) for e in edges]  # make a shallow copy
    new_vertex = n
    for v in range(n):
        new_edges.append([new_vertex, v])

    return {"n": n + 1, "edges": new_edges}

