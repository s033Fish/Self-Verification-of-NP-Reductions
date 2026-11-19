"""Reduction from 3‑SAT to Clique.

The source problem (ThreeSat) uses the format:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
where each literal is an integer ``+v`` (variable ``v`` true) or ``-v``
(variable ``v`` false).  All clauses contain exactly three literals on
distinct variables.

The target problem (Clique) expects a graph instance:
    {"n": n, "edges": [[u, v], ...], "k": k}
with vertices ``0..n-1`` and an undirected edge list.  The answer is *yes*
iff the graph contains a clique of size at least ``k``.

Standard polynomial‑time reduction:

* For each clause create three vertices – one for each literal.
* Connect two vertices with an edge **iff** they belong to different
  clauses *and* the corresponding literals are not contradictory
  (i.e. they are not of the form ``x`` and ``-x``).
* Set ``k`` to the number of clauses.  A clique of size ``k`` selects one
  literal from each clause and they are pairwise compatible, which is
  exactly a satisfying assignment.

The reduction also correctly handles the edge case of an empty formula.
When there are no clauses the formula is trivially satisfiable; we return
``k = 0`` (always a yes‑instance) and an empty graph.

The function runs in ``O(c^2)`` time where ``c`` is the number of clauses,
well within polynomial bounds.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ThreeSat specification.

    Returns
    -------
    dict
        A dictionary conforming to the Clique specification such that
        the Clique instance is a *yes*‑instance exactly when the original
        3‑SAT instance is satisfiable.
    """

    # Extract data from the SAT instance.
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build a list of (clause_index, literal) for each vertex.
    # Vertex IDs will be their position in this list.
    vertices: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        # According to the specification each clause has exactly three literals.
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    k = num_clauses

    # Construct edges between compatible vertices from different clauses.
    edges: List[List[int]] = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                # No edges within the same clause.
                continue
            # Skip contradictory literals (x and ¬x).
            if li == -lj:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": k}

