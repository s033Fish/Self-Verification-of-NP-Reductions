"""Reduction from 3‑SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  A
literal is an integer ``+v`` (variable *v* should be true) or ``-v``
*(variable *v* should be false).  Every clause contains exactly three
different variables.

The target problem is ``IndependentSet`` with an instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.  Vertices are numbered
``0 .. n‑1`` and ``k`` is the required size of the independent set.

Standard polynomial‑time reduction:

* For each clause we create a triangle (3 vertices, all pairwise
  adjacent).  Selecting at most one vertex from each triangle ensures we
  pick at most one literal per clause.
* For any two vertices that correspond to complementary literals
  (e.g. ``+x`` and ``-x``) we add an edge, preventing them from both being
  chosen.
* We set ``k`` equal to the number of clauses.  An independent set of size
  ``k`` exists iff we can pick one non‑conflicting literal from each
  clause, i.e. the formula is satisfiable.

The implementation below follows this construction.  It runs in time
``O(C^2)`` where ``C`` is the number of clauses, which is polynomial in the
size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as
        described in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance with keys ``"n"``, ``"edges"`` and
        ``"k"``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Each clause contributes three vertices: one per literal.
    n = 3 * num_clauses
    k = num_clauses  # we need to pick exactly one vertex per clause

    # Helper to collect edges without duplicates.
    edge_set = set()

    # 1. Add triangle edges inside each clause.
    for ci, clause in enumerate(clauses):
        base = 3 * ci
        v0, v1, v2 = base, base + 1, base + 2
        for u, v in ((v0, v1), (v0, v2), (v1, v2)):
            if u > v:
                u, v = v, u
            edge_set.add((u, v))

    # 2. Add conflict edges for complementary literals across clauses.
    # Build a list of (var, sign, vertex) entries.
    literal_vertices: List[Tuple[int, bool, int]] = []
    for ci, clause in enumerate(clauses):
        base = 3 * ci
        for offset, lit in enumerate(clause):
            var = abs(lit)
            sign = lit > 0  # True for positive, False for negative
            vertex = base + offset
            literal_vertices.append((var, sign, vertex))

    L = len(literal_vertices)
    for i in range(L):
        var_i, sign_i, v_i = literal_vertices[i]
        for j in range(i + 1, L):
            var_j, sign_j, v_j = literal_vertices[j]
            # Skip pairs from the same clause (already fully connected)
            if v_i // 3 == v_j // 3:
                continue
            # Add edge if literals are complementary on the same variable
            if var_i == var_j and sign_i != sign_j:
                u, v = (v_i, v_j) if v_i < v_j else (v_j, v_i)
                edge_set.add((u, v))

    edges = [[u, v] for (u, v) in sorted(edge_set)]

    return {"n": n, "edges": edges, "k": k}

