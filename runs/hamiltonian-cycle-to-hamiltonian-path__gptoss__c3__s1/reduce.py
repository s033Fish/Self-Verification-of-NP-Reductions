"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

We use the classic *vertex‑splitting* reduction.
For a graph G = (V, E) with |V| = n (n ≥ 3) we construct a graph G' as follows:

* For each vertex i ∈ V create two vertices i_in and i_out.
  We label i_in as i and i_out as i + n.
* Add the “internal” edge (i_in, i_out) for every i.
* For every original edge {u, v} ∈ E add the “cross” edges
  (u_out, v_in) and (v_out, u_in).

G' has 2n vertices.  It is easy to see that G contains a Hamiltonian
cycle iff G' contains a Hamiltonian *path* (the endpoints of the path are
0_in and 0_out, but the target problem allows any endpoints, so this is fine).
The construction is polynomial‑time and works for all instances.
For the trivial cases n ≤ 2 the source problem is always a "no" instance;
we therefore return a trivially "no" target instance (the empty graph).
"""

from __future__ import annotations

from typing import Any, Dict, List, Set

from problems import SOURCE, TARGET


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    The returned instance is a yes‑instance exactly when the input instance is
    a yes‑instance.
    """
    # Validate source instance.
    SOURCE.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial cases: source is always "no" for n <= 2.
    if n <= 2:
        trivial: Dict[str, Any] = {"n": 0, "edges": []}
        TARGET.validate(trivial)
        return trivial

    new_n = 2 * n
    edge_set: Set[frozenset[int]] = set()

    def add(u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loop not allowed")
        edge_set.add(frozenset((u, v)))

    # Internal edges (i_in, i_out).
    for i in range(n):
        add(i, i + n)

    # Cross edges for each original edge.
    for u, v in edges:
        # u_out = u + n, v_in = v
        add(u + n, v)
        # v_out = v + n, u_in = u
        add(v + n, u)

    # Convert edge_set to the list format required by the problem.
    new_edges: List[List[int]] = [list(e) for e in edge_set]

    result: Dict[str, Any] = {"n": new_n, "edges": new_edges}
    TARGET.validate(result)
    return result

