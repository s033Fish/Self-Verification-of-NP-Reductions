"""Reduction from 3‑SAT to Vertex Cover.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (the variable ``v`` is true) or
``-v`` (the variable ``v`` is false).  Every clause contains three distinct
variables.

The target problem is ``VertexCover`` with an instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction is the classic textbook construction:

* For each variable ``x_i`` create two vertices ``i_T`` and ``i_F`` and an edge
  between them.  In any vertex cover at least one of the two must be chosen –
  we interpret the chosen vertex as the *false* assignment for that variable.
* For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` create a triangle of three new vertices.
  Picking two vertices of the triangle covers its three internal edges; the
  remaining vertex corresponds to the literal that satisfies the clause.
* Connect each clause‑literal vertex to the vertex representing the same
  literal in the variable gadget (true‑vertex for a positive literal, false‑
  vertex for a negative literal).

With ``m`` variables and ``c`` clauses the constructed graph has
``n = 2*m + 3*c`` vertices.  The required vertex‑cover size is
``k = m + 2*c`` – one vertex per variable edge and two vertices per clause
triangle.  It is easy to see that the original formula is satisfiable iff the
graph admits a vertex cover of size at most ``k``.

The ``reduce`` function below implements this construction in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers representing literals).

    Returns
    -------
    dict
        A Vertex‑Cover instance ``{"n": n, "edges": edges, "k": k}``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex numbering:
    #   variable true  : 2*i   (i from 0 to m-1)
    #   variable false : 2*i+1
    #   clause literals: start at 2*m, three per clause.
    var_true = lambda i: 2 * i          # i is 0‑based variable index
    var_false = lambda i: 2 * i + 1

    edges: List[List[int]] = []

    # 1. Variable edges (ensure at least one endpoint is chosen).
    for i in range(m):
        u = var_true(i)
        v = var_false(i)
        edges.append([u, v])

    # 2. Clause triangles and connections to variable vertices.
    base_clause = 2 * m
    for ci, clause in enumerate(clauses):
        # clause vertices ids
        a = base_clause + 3 * ci
        b = a + 1
        c_id = a + 2

        # triangle edges
        edges.append([a, b])
        edges.append([b, c_id])
        edges.append([a, c_id])

        # connections for each literal
        for lit_idx, lit in enumerate(clause):
            var = abs(lit) - 1  # convert to 0‑based variable index
            if var < 0 or var >= m:
                # Defensive: ignore literals referencing non‑existent variables.
                # The input specification guarantees this cannot happen.
                continue
            clause_vertex = a + lit_idx
            if lit > 0:
                # positive literal → connect to true vertex
                target = var_true(var)
            else:
                # negative literal → connect to false vertex
                target = var_false(var)
            # store edge with smaller vertex first for consistency
            if clause_vertex < target:
                edges.append([clause_vertex, target])
            else:
                edges.append([target, clause_vertex])

    n = 2 * m + 3 * c
    k = m + 2 * c

    # Ensure there are no duplicate edges (the construction does not create any,
    # but we deduplicate just in case).
    seen = set()
    uniq_edges: List[List[int]] = []
    for u, v in edges:
        if u == v:
            # self‑loops are irrelevant for vertex cover; skip them.
            continue
        if u > v:
            u, v = v, u
        if (u, v) not in seen:
            seen.add((u, v))
            uniq_edges.append([u, v])

    return {"n": n, "edges": uniq_edges, "k": k}

