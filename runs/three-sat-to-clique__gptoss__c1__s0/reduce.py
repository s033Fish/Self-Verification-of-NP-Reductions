"""Reduction from 3‑SAT to CLIQUE.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
following instance format::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Each literal is a string ``"+v"`` (variable *v* is true) or ``"-v"`` (variable
*v* is false).  Every clause contains exactly three literals on distinct
variables.

The target problem is ``Clique`` with instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 … n‑1`` and edges are undirected.  The instance is a
*yes* instance iff the graph contains a clique of size **at least** ``k``.

Standard polynomial‑time reduction:

* Create a vertex for every literal in every clause (so ``3 * #clauses``
  vertices).
* Connect two vertices **iff** they belong to different clauses *and* the two
  literals are not contradictory (i.e. they are not ``+v`` and ``-v`` for the
  same variable).
* Set ``k`` to the number of clauses.

If the formula has no clauses the reduction must still produce a yes‑instance
for CLIQUE.  Because ``k <= 0`` is always a yes‑instance, we simply return a
graph with ``n = 0`` and ``k = 0``.

The implementation below follows exactly this construction and runs in
polynomial time with respect to the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _is_complement(lit1: str, lit2: str) -> bool:
    """Return ``True`` if ``lit1`` and ``lit2`` are opposite literals of the same variable.

    Literals are of the form ``"+v"`` or ``"-v"`` where ``v`` is a positive
    integer.  Two literals are complementary when they refer to the same
    variable and have opposite signs.
    """
    # The first character encodes the sign, the rest the variable number.
    sign1, var1 = lit1[0], lit1[1:]
    sign2, var2 = lit2[0], lit2[1:]
    return var1 == var2 and sign1 != sign2


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a CLIQUE instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"num_vars"`` and ``"clauses"`` as described in
        the problem statement.

    Returns
    -------
    dict
        A CLIQUE instance ``{"n": n, "edges": [...], "k": k}`` such that the
        CLIQUE instance is a *yes* instance iff the original 3‑SAT instance is
        satisfiable.
    """
    clauses: List[List[str]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for each literal in each clause.
    # We'll store literals in a list indexed by vertex id.
    vertex_literals: List[str] = []  # index -> literal string
    clause_of_vertex: List[int] = []  # which clause the vertex belongs to
    for ci, clause in enumerate(clauses):
        # Each clause is guaranteed to have exactly three literals.
        for lit in clause:
            vertex_literals.append(lit)
            clause_of_vertex.append(ci)

    n = len(vertex_literals)  # should be 3 * num_clauses
    k = num_clauses

    edges: List[Tuple[int, int]] = []
    # Add edges between vertices of different clauses that are not complementary.
    for u in range(n):
        for v in range(u + 1, n):
            if clause_of_vertex[u] == clause_of_vertex[v]:
                # Same clause – no edge.
                continue
            lit_u = vertex_literals[u]
            lit_v = vertex_literals[v]
            if _is_complement(lit_u, lit_v):
                continue
            edges.append((u, v))

    # Convert edge tuples to the required list format.
    edge_list: List[List[int]] = [[u, v] for (u, v) in edges]

    return {"n": n, "edges": edge_list, "k": k}

