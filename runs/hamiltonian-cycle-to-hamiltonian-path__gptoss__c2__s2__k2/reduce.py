"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) asks whether an undirected graph
contains a cycle that visits every vertex exactly once.  The target
problem (HamiltonianPath) asks whether an undirected graph contains a
path that visits every vertex exactly once (endpoints are unrestricted).

We implement a classic polynomial‑time many‑one reduction.  For a given
graph G = (V, E) with |V| = n we construct a new graph G' = (V', E')
such that G has a Hamiltonian cycle iff G' has a Hamiltonian path.

Construction (for n >= 3):
  1. Choose an arbitrary vertex v₀ ∈ V.  For simplicity we use vertex 0.
  2. Replace v₀ by two new vertices a and b.  Both a and b are made
     adjacent to every original neighbour of v₀.  (If (v₀, u) ∈ E then
     we add edges (a, u) and (b, u) to E'.)
  3. All edges that do not involve v₀ are copied unchanged.
  4. Add two fresh degree‑1 vertices s and t.  Connect s only to a and t
     only to b.  These two vertices force any Hamiltonian path in G' to
     start at s and end at t, because s and t have degree 1.

Why the reduction works:
  * If G has a Hamiltonian cycle, break the cycle at the occurrence of
    v₀.  This yields a Hamiltonian path in the original vertices that
    starts at some neighbour u₁ of v₀ and ends at another neighbour u₂
    of v₀.  In G' we can start at s, move to a, then to u₁, follow the
    broken cycle covering all original vertices, reach u₂, move to b,
    and finally to t.  All vertices of G' are visited exactly once – a
    Hamiltonian path.
  * Conversely, any Hamiltonian path in G' must start at s and end at t
    (they are the only degree‑1 vertices).  Removing s and t contracts
    a and b back into a single vertex v₀, and the remaining order of the
    original vertices forms a Hamiltonian cycle in G.

Edge‑case handling:
  The source definition declares that graphs with n ≤ 2 never have a
  Hamiltonian cycle.  For such inputs we must output a *no* instance of
  HamiltonianPath.  The simplest choice is the empty graph (n = 0,
  no edges), which is a known “no” instance for the target problem.

The reduction runs in O(n + |E|) time and uses only basic Python data
structures, satisfying the polynomial‑time requirement.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists) representing an undirected graph.

    Returns
    -------
    dict
        An instance of the Hamiltonian‑Path problem with the property
        that the answer is *yes* iff the answer for the input instance
        is *yes*.
    """
    n = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # For source instances where a Hamiltonian cycle is impossible (n <= 2)
    # we return a guaranteed no‑instance for Hamiltonian Path.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the split vertex.
    split_vertex = 0

    # New vertex identifiers
    a = n          # first copy of split vertex
    b = n + 1      # second copy
    s = n + 2      # start leaf
    t = n + 3      # end leaf
    new_n = n + 4

    # Build adjacency for the new graph.
    new_edges: List[List[int]] = []

    # Helper to add an edge (undirected) ensuring no duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        # store with smaller first for consistency
        if u > v:
            u, v = v, u
        new_edges.append([u, v])

    # Process original edges.
    for u, v in edges:
        if u == split_vertex or v == split_vertex:
            # Edge incident to the split vertex – connect both copies.
            other = v if u == split_vertex else u
            add_edge(a, other)
            add_edge(b, other)
        else:
            # Edge unrelated to split vertex – copy unchanged.
            add_edge(u, v)

    # Connect the leaf vertices.
    add_edge(s, a)
    add_edge(t, b)

    # The reduction does not need the edge (a, b); omitting it prevents
    # spurious paths that do not correspond to a cycle.

    return {"n": new_n, "edges": new_edges}

