"""Reduction from 3-Coloring to SAT.

The source problem is defined in ``problems.py`` as ``ThreeColoring`` with
instance format ``{"n": n, "edges": [[u, v], ...]}``.  The target problem is
``Sat`` with instance format ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.

For each vertex ``i`` (0‑based) we introduce three Boolean variables that encode
whether the vertex receives colour 0, 1 or 2.  Variables are numbered starting
at 1 as required by the SAT format:

    var(i, c) = i * 3 + c + 1   (c in {0,1,2})

The CNF formula consists of three families of clauses:

1. **Each vertex gets at least one colour** – a single clause containing the
   three positive literals for that vertex.
2. **Each vertex gets at most one colour** – for every unordered pair of
   colours ``c < d`` we add a clause ``(-var(i,c) ∨ -var(i,d))``.
3. **Adjacent vertices receive different colours** – for every edge ``(u, v)``
   and each colour ``c`` we add ``(-var(u,c) ∨ -var(v,c))``.

The construction uses ``3 * n`` variables and a number of clauses that is
polynomial in ``n`` and the number of edges, satisfying the polynomial‑time
requirement.

The ``reduce`` function follows the conventions used throughout the repository:
it receives a source instance (a ``dict``) and returns a target instance (also a
``dict``).  No solver is invoked; the function merely builds the CNF.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        ``{"n": int, "edges": List[List[int]]}`` describing an undirected
        simple graph with vertices ``0 .. n-1``.

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": List[List[int]]}`` representing a CNF
        formula that is satisfiable iff the input graph is 3‑colorable.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Number of Boolean variables: three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # Helper to compute the variable number for vertex i and colour c.
    def var(i: int, c: int) -> int:
        # Variables are 1‑based.
        return i * 3 + c + 1

    # 1. At least one colour per vertex.
    for i in range(n):
        clauses.append([var(i, 0), var(i, 1), var(i, 2)])

    # 2. At most one colour per vertex (pairwise mutual exclusion).
    for i in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-var(i, c1), -var(i, c2)])

    # 3. Adjacent vertices must not share the same colour.
    for u, v in edges:
        # The instance guarantees u != v and edges are undirected; we add the
        # constraint for each colour.
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

