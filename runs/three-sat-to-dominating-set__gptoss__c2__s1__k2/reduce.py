"""Reduction from 3‑SAT to Dominating Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable ``v`` set to true) or
``-v`` (variable ``v`` set to false).  Every clause contains three distinct
variables.

The target problem is ``DominatingSet`` with the instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction is the classic polynomial‑time construction that creates a
variable gadget (a single edge) for each variable and a clause gadget (a
triangle) for each clause.  Each vertex of a clause triangle is connected to
the vertex representing the corresponding literal.  With ``k = m + c`` (where
``c`` is the number of clauses) the formula is satisfiable iff the constructed
graph has a dominating set of size at most ``k``.

The construction works for all edge cases mentioned in the doc‑strings:

* If there are no clauses, the graph consists only of the variable edges.
  Selecting one endpoint of each variable edge gives a dominating set of
  size ``m`` which equals ``k``.
* If ``m = 0`` the graph is empty (``n = 0``) and ``k = 0`` – trivially a
  yes‑instance.

The function ``reduce`` implements this transformation in linear time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers).

    Returns
    -------
    dict
        A dominating‑set instance ``{"n": n, "edges": [...], "k": k}``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex numbering:
    #   For variable i (1‑based) we create two vertices:
    #       true_id  = 2 * (i‑1)
    #       false_id = 2 * (i‑1) + 1
    #   Clause vertices start after the 2*m variable vertices.
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # Variable gadgets: a single edge between true and false vertex.
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Clause gadgets.
    base_clause = 2 * m  # first clause vertex index
    for j, clause in enumerate(clauses):
        # The three vertices of the clause triangle.
        v0 = base_clause + 3 * j
        v1 = v0 + 1
        v2 = v0 + 2
        # Triangle edges.
        edges.append([v0, v1])
        edges.append([v1, v2])
        edges.append([v0, v2])

        # Connect each clause vertex to the corresponding literal vertex.
        for offset, lit in enumerate(clause):
            var = abs(lit)
            if lit > 0:
                lit_vertex = var_true(var)
            else:
                lit_vertex = var_false(var)
            clause_vertex = v0 + offset
            edges.append([clause_vertex, lit_vertex])

    n = 2 * m + 3 * c
    k = m + c

    # Ensure edges are undirected and each appears only once. The construction
    # never adds duplicate edges, but we normalise the order (u < v) for
    # consistency with the problem specification.
    normalised_edges: List[List[int]] = []
    seen = set()
    for u, v in edges:
        if u == v:
            # No self‑loops in the definition; skip if ever created.
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in seen:
            seen.add((a, b))
            normalised_edges.append([a, b])

    return {"n": n, "edges": normalised_edges, "k": k}

