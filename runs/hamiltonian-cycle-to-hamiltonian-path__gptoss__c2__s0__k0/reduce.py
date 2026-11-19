"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) asks whether an undirected graph has a
Hamiltonian cycle.  The target problem (HamiltonianPath) asks whether there is
a Hamiltonian path (endpoints may be any vertices).

Reduction idea (standard):
  * Pick an arbitrary vertex v (we use vertex 0 if it exists).
  * Remove v from the graph.
  * Add two new vertices s and t.
  * Connect s and t to every former neighbor of v.
  * Keep all other edges unchanged (re‑indexed after the removal of v).

If the original graph G has a Hamiltonian cycle, then after deleting v we get a
Hamiltonian path between two neighbors a and b of v.  Adding s adjacent to a
and t adjacent to b yields a Hamiltonian path from s to t in the new graph G'.
Conversely, any Hamiltonian path from s to t in G' must start at a neighbor of v
(via s) and end at a (possibly different) neighbor of v (via t).  Removing s and
t restores a Hamiltonian path on the original vertices except v, which can be
closed into a Hamiltonian cycle by inserting v between its two endpoints.
Thus G has a Hamiltonian cycle iff G' has a Hamiltonian path.

Edge cases:
  * For n <= 2 the source problem is always a NO instance.  We return a
    trivially NO instance for HamiltonianPath (n = 0, no edges).

The reduction runs in linear time in the size of the input graph.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance.

    Parameters
    ----------
    instance: dict
        Must contain keys "n" (int) and "edges" (list of [u, v]).

    Returns
    -------
    dict
        An instance for HamiltonianPath with the same format.
    """

    n = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge cases: for n <= 2 the source problem is always NO.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the distinguished vertex v.
    v = 0
    neighbor_set = set()
    other_edges: List[List[int]] = []
    for u, w in edges:
        if u == v:
            neighbor_set.add(w)
        elif w == v:
            neighbor_set.add(u)
        else:
            other_edges.append([u, w])

    # Re‑index remaining vertices (all except v) to a contiguous range 0..n-2.
    old_to_new: Dict[int, int] = {}
    cur = 0
    for old in range(n):
        if old == v:
            continue
        old_to_new[old] = cur
        cur += 1
    # cur == n-1 now.
    s = cur          # first new vertex index
    t = cur + 1      # second new vertex index
    new_n = cur + 2  # total vertices after adding s and t

    # Translate edges that did not involve v.
    new_edges: List[List[int]] = []
    for u, w in other_edges:
        new_edges.append([old_to_new[u], old_to_new[w]])

    # Connect s and t to every neighbor of v (using new indices).
    for old_u in neighbor_set:
        new_u = old_to_new[old_u]
        new_edges.append([s, new_u])
        new_edges.append([t, new_u])

    return {"n": new_n, "edges": new_edges}

