"""Reduction from 3‑SAT to Vertex Cover.

The source problem is defined by the ``ThreeSat`` class (see ``problems.py``):

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal is an integer ``+v`` (meaning variable *v* is true) or
``-v`` (meaning variable *v* is false).  Every clause contains three distinct
variables.

The target problem is ``VertexCover`` with instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction used here is the classic one described in many textbooks.

Construction
==============

* **Variable vertices** – For each variable ``i`` (1‑based) we create two
  vertices ``T_i`` and ``F_i`` representing the literal ``+i`` and ``-i``
  respectively.  An edge ``[T_i, F_i]`` forces a vertex cover to contain at
  least one of the two, which we interpret as fixing the truth value of the
  variable.

* **Clause gadget** – For each clause we create a triangle of three new
  vertices ``C_{j,0}``, ``C_{j,1}``, ``C_{j,2}``.  A triangle needs at least two
  vertices in any vertex cover; the remaining (uncovered) vertex will be the
  one that “satisfies’’ the clause.

* **Literal‑clause connections** – The *p*‑th vertex of the clause triangle is
  connected to the variable vertex that corresponds to the literal appearing
  in that position.  If the literal is ``+v`` we connect to ``T_v``; if it is
  ``-v`` we connect to ``F_v``.

If the original formula is satisfiable, we can select for each variable the
vertex that matches the satisfying assignment and, for each clause, choose the
triangle vertex that is adjacent to a selected literal vertex.  Together with
the two remaining vertices of the triangle we obtain a vertex cover of size
``m + 2·c`` where ``c`` is the number of clauses.

Conversely, any vertex cover of size at most ``m + 2·c`` must contain exactly
one endpoint of each variable edge (otherwise we would need more than ``m``
vertices) and exactly two vertices from each clause triangle.  The uncovered
triangle vertex is forced to be adjacent to a selected literal vertex, which
gives a satisfying assignment.

Thus the formula is satisfiable iff the constructed graph has a vertex cover
of size ``k = m + 2·c``.

The implementation below follows this construction and runs in polynomial
time with respect to the size of the 3‑SAT instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers).

    Returns
    -------
    dict
        A Vertex Cover instance ``{"n": n, "edges": [...], "k": k}``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex numbering:
    #   for variable i (1‑based): true vertex = 2*(i-1), false vertex = 2*(i-1)+1
    #   clause vertices start after the 2*m variable vertices.
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # 1. Variable edges (force a choice per variable)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Base index for clause vertices
    clause_base = 2 * m

    for j, clause in enumerate(clauses):
        # vertices of the triangle for clause j
        v0 = clause_base + 3 * j
        v1 = v0 + 1
        v2 = v0 + 2

        # add the three edges of the triangle
        edges.append([v0, v1])
        edges.append([v0, v2])
        edges.append([v1, v2])

        # connect each clause vertex to the appropriate literal vertex
        for pos, lit in enumerate(clause):
            var = abs(lit)
            if var == 0:
                # Defensive: literals are 1‑based per specification.
                continue
            # Determine which variable vertex corresponds to the literal
            literal_vertex = var_true(var) if lit > 0 else var_false(var)
            clause_vertex = v0 + pos  # pos is 0,1,2
            edges.append([clause_vertex, literal_vertex])

    n = clause_base + 3 * c  # total number of vertices
    k = m + 2 * c            # size bound for the vertex cover

    # Ensure edges are undirected and each edge appears only once with u < v
    normalized_edges: List[List[int]] = []
    seen = set()
    for u, v in edges:
        if u == v:
            # ignore self‑loops (should not happen)
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in seen:
            seen.add((a, b))
            normalized_edges.append([a, b])

    return {"n": n, "edges": normalized_edges, "k": k}

