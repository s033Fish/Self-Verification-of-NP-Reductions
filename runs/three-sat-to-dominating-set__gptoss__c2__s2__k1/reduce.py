"""Reduction from 3‑SAT to Dominating Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  A
literal is represented by a signed integer: ``+v`` means the variable *v*
is true, ``-v`` means it is false.

The target problem is ``DominatingSet`` with instance format
``{"n": n, "edges": [[u, v], ...], "k": k}`` where vertices are numbered
``0..n-1`` and edges are undirected.

We implement the classic polynomial‑time reduction described in many
textbooks (e.g., Garey & Johnson).  For each variable ``x_i`` we create two
vertices ``x_i^T`` and ``x_i^F`` and connect them with an edge.  For each
clause ``C_j = (ℓ_1 ∨ ℓ_2 ∨ ℓ_3)`` we create a triangle of three new vertices
``c_{j,1}, c_{j,2}, c_{j,3}``.  The *k*‑th vertex of the triangle is connected
to the vertex representing the literal ``ℓ_k`` (the true‑literal vertex if the
literal is positive, otherwise the false‑literal vertex).

Let ``m`` be the number of variables and ``c`` the number of clauses.  The
constructed graph has ``n = 2*m + 3*c`` vertices and we set ``k = m + c``.

Correctness sketch:
* If the formula is satisfiable, pick for each variable the vertex that
  corresponds to the truth assignment (true literal vertex for true, false
  literal vertex otherwise).  This gives ``m`` vertices that dominate the
  variable edges.  In each clause at least one literal is true, so the
  corresponding clause‑triangle vertex is adjacent to a selected literal
  vertex and therefore dominates the whole triangle.  The set size is
  ``m + c`` and dominates the whole graph.
* Conversely, any dominating set of size at most ``m + c`` can be transformed
  into one that contains exactly one vertex from each variable edge and at
  most one vertex from each clause triangle.  Interpreting the chosen literal
  vertices as a truth assignment satisfies every clause, otherwise the
  clause triangle would require two vertices, exceeding the size bound.

The reduction runs in time polynomial in the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}``
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex indices:
    #   true literals:   0 .. m-1          (index = var-1)
    #   false literals:  m .. 2*m-1      (index = m + var-1)
    #   clause vertices: start at 2*m, three per clause
    true_idx = lambda var: var - 1
    false_idx = lambda var: m + var - 1

    edges_set: Set[Tuple[int, int]] = set()

    # Variable edges (xi^T -- xi^F)
    for var in range(1, m + 1):
        u = true_idx(var)
        v = false_idx(var)
        edges_set.add((min(u, v), max(u, v)))

    # Clause gadgets
    base_clause = 2 * m
    for j, clause in enumerate(clauses):
        # clause should have exactly three literals
        if len(clause) != 3:
            # The problem definition guarantees this, but we handle it
            # gracefully by skipping malformed clauses.
            continue
        # indices of the three clause vertices
        c0 = base_clause + 3 * j
        c1 = c0 + 1
        c2 = c0 + 2
        # triangle edges among clause vertices
        for (u, v) in [(c0, c1), (c1, c2), (c2, c0)]:
            edges_set.add((min(u, v), max(u, v)))
        # connect each clause vertex to the appropriate literal vertex
        literals = clause
        for offset, lit in enumerate(literals):
            var = abs(lit)
            if var == 0 or var > m:
                # ignore out‑of‑range literals (should not happen)
                continue
            if lit > 0:
                lit_vertex = true_idx(var)
            else:
                lit_vertex = false_idx(var)
            clause_vertex = base_clause + 3 * j + offset
            edges_set.add((min(lit_vertex, clause_vertex), max(lit_vertex, clause_vertex)))

    # Convert edge set to required list format
    edges: List[List[int]] = [[u, v] for (u, v) in sorted(edges_set)]
    n = 2 * m + 3 * c
    k = m + c

    return {"n": n, "edges": edges, "k": k}

