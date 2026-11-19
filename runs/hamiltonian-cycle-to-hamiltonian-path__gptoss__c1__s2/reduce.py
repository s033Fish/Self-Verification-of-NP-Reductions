"""Reduction from Hamiltonian Cycle (SOURCE) to Hamiltonian Path (TARGET).

The source problem expects an undirected graph given by {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0 … n‑1.  A *Hamiltonian cycle* is a cycle that
visits every vertex exactly once and returns to the start.

The target problem expects the same format but asks for a *Hamiltonian path* –
any simple path that visits every vertex exactly once (endpoints are free).

Standard polynomial‑time reduction:
    • Choose an arbitrary vertex v₀ (we use 0).
    • Remove v₀ from the graph.
    • Introduce two new vertices s and t.
    • Connect s and t to every former neighbour of v₀.
    • Keep all other edges unchanged (between the remaining vertices).

If the original graph has a Hamiltonian cycle, breaking the cycle at v₀ yields a
Hamiltonian path between the two neighbours of v₀; the added vertices s and t
can be attached to the endpoints, giving a Hamiltonian path in the new graph.
Conversely, any Hamiltonian path from s to t in the constructed graph can be
closed by re‑inserting v₀ between the neighbours that are adjacent to s and t,
producing a Hamiltonian cycle in the original graph.

Edge‑case handling:
    – For n ≤ 2 the source instance is always a NO‑instance (as specified).
      We return a trivially unsatisfiable target instance {"n": 0, "edges": []}
      which is a NO‑instance for Hamiltonian Path.

The function runs in O(n + |E|) time and uses only standard Python data
structures.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "n" (int) and "edges" (list of
        two‑element lists) describing an undirected graph.

    Returns
    -------
    dict
        An instance of the Hamiltonian‑Path problem that is a YES‑instance
        exactly when the input is a YES‑instance.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial NO‑instances for the source (n <= 2).  Return a trivial NO for the target.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the distinguished vertex v0.
    v0 = 0

    # Determine neighbours of v0 and collect edges that do not involve v0.
    neighbours: Set[int] = set()
    other_edges: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v0:
            neighbours.add(v)
        elif v == v0:
            neighbours.add(u)
        else:
            a, b = (u, v) if u < v else (v, u)
            other_edges.add((a, b))

    # Mapping from old vertex id (excluding v0) to new contiguous ids.
    # Old vertices 1..n-1 become 0..n-2.
    old_to_new: Dict[int, int] = {}
    new_id = 0
    for old in range(n):
        if old == v0:
            continue
        old_to_new[old] = new_id
        new_id += 1

    # New vertices s and t will be placed after the reindexed original vertices.
    s = new_id  # first new vertex
    t = new_id + 1  # second new vertex
    new_n = new_id + 2

    new_edges: List[List[int]] = []

    # Add the edges among the remaining original vertices.
    for a, b in other_edges:
        new_a = old_to_new[a]
        new_b = old_to_new[b]
        new_edges.append([new_a, new_b])

    # Connect s and t to every former neighbour of v0.
    for nb in neighbours:
        new_nb = old_to_new[nb]
        new_edges.append([s, new_nb])
        new_edges.append([t, new_nb])

    return {"n": new_n, "edges": new_edges}

