"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (Hamiltonian Cycle) is defined on an undirected graph
with vertices ``0..n-1``.  The target problem (Hamiltonian Path) uses the same
format but asks for a path (any endpoints) that visits every vertex exactly
once.

Standard textbook reduction:
    Given a graph G = (V, E) with |V| = n, create a new graph G' = (V', E')
    where V' = V ∪ {s} (add a fresh vertex ``s``) and
    E' = E ∪ { {s, v} : v ∈ V } (connect ``s`` to every original vertex).

If G contains a Hamiltonian *cycle*, removing any edge of that cycle and
using ``s`` as the break point yields a Hamiltonian *path* in G'.  Conversely,
any Hamiltonian path in G' must start or end at ``s`` (because ``s`` has degree
``n`` and all other vertices have degree at most ``n-1``).  Deleting ``s`` from
the path leaves a Hamiltonian cycle in the original graph.  This equivalence
holds for all graphs with n ≥ 3.  For the trivial edge‑cases (n ≤ 2) the source
problem is defined to be a definite ``NO``; we therefore output a target
instance that is also a definite ``NO`` (an empty graph).

The function ``reduce(instance)`` implements this transformation.  It runs
in linear time with respect to the size of the input instance.
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
        the answer is *yes* exactly when the answer for the input instance is
        *yes*.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge cases: for n <= 2 the source problem is always NO.  We return a
    # target instance that is also a definite NO (empty graph).
    if n <= 2:
        return {"n": 0, "edges": []}

    # Construct the new graph with an additional vertex s = n.
    new_n = n + 1
    new_edges = [list(e) for e in edges]  # copy original edges
    # Connect the new vertex to every original vertex.
    for v in range(n):
        new_edges.append([n, v])

    return {"n": new_n, "edges": new_edges}

