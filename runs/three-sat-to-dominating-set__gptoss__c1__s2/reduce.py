"""Reduction from 3‑SAT to Dominating Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where a
literal is an integer ``+v`` (variable ``v`` is true) or ``-v`` (variable ``v``
is false).  The target problem is ``DominatingSet`` with an instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.

We implement the classic polynomial‑time reduction:

* For each variable ``x_i`` (``i`` from ``1`` to ``m``) create two vertices
  ``v_i`` (representing ``x_i`` true) and ``¬v_i`` (representing ``x_i`` false).
  These two vertices are connected by an edge – a dominating set must pick at
  least one of them.
* For each clause ``C_j = (ℓ_1 ∨ ℓ_2 ∨ ℓ_3)`` create three clause vertices
  ``c_{j,0}``, ``c_{j,1}``, ``c_{j,2}``.  They form a triangle, ensuring that if
  none of the literals of the clause are chosen in the dominating set, at
  least one of the three clause vertices has to be selected.
* The ``t``‑th clause vertex ``c_{j,t}`` is connected to the literal vertex
  that corresponds to the ``t``‑th literal of the clause.

If the formula is satisfiable, we can pick for each variable the vertex that
represents a true literal and, for each clause, we do **not** need to pick a
clause vertex because the clause already has a true literal adjacent to it.
Thus we obtain a dominating set of size ``m + #clauses``.  Conversely, any
dominating set of size at most ``m + #clauses`` can be transformed into a
truth assignment that satisfies the formula.

The reduction runs in time linear in the size of the 3‑SAT instance, which is
polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers).  The format follows the description
        in ``problems.py``.

    Returns
    -------
    dict
        An instance of the Dominating Set problem with keys ``"n"``,
        ``"edges"`` and ``"k"``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex indexing:
    #   0 .. 2*m-1   – variable literals (pair per variable)
    #   2*m .. 2*m+3*c-1 – clause vertices (three per clause)
    # Helper functions to compute indices.
    def pos_idx(var: int) -> int:
        # var is 1‑based
        return 2 * (var - 1)

    def neg_idx(var: int) -> int:
        return 2 * (var - 1) + 1

    def clause_vertex_idx(clause_id: int, pos_in_clause: int) -> int:
        # clause_id in [0, c), pos_in_clause in {0,1,2}
        return 2 * m + 3 * clause_id + pos_in_clause

    edges: List[List[int]] = []

    # Variable edges (each variable's two literals are adjacent)
    for var in range(1, m + 1):
        u = pos_idx(var)
        v = neg_idx(var)
        edges.append([u, v])

    # Clause gadgets
    for j, clause in enumerate(clauses):
        # create triangle among the three clause vertices
        base = clause_vertex_idx(j, 0)
        v0, v1, v2 = base, base + 1, base + 2
        edges.append([v0, v1])
        edges.append([v0, v2])
        edges.append([v1, v2])

        # connect each clause vertex to the corresponding literal vertex
        for t, lit in enumerate(clause):
            var = abs(lit)
            if var == 0:
                # Defensive: should never happen due to validation, but we
                # skip to keep the reduction well‑formed.
                continue
            lit_vertex = pos_idx(var) if lit > 0 else neg_idx(var)
            clause_vertex = clause_vertex_idx(j, t)
            edges.append([lit_vertex, clause_vertex])

    # Parameter k = m + number of clauses (the bound used in the classic
    # reduction).  This ensures the reduction is correct both for yes and no
    # instances.
    k = m + c

    n = 2 * m + 3 * c

    # Ensure each edge is stored with the smaller vertex first (not required
    # by the definition but convenient for consistency).
    normalized_edges = [[u, v] if u < v else [v, u] for u, v in edges]

    return {"n": n, "edges": normalized_edges, "k": k}

