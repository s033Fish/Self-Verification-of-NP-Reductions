"""Reduction from 3‑SAT to Vertex Cover.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Every clause contains exactly three
distinct literals on distinct variables.

The target problem is ``VertexCover`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction follows the classic polynomial‑time construction used in many
textbooks:

* For each variable ``i`` (1‑indexed) create two vertices ``i_T`` and ``i_F``
  that are connected by an edge.  In any vertex cover of size ``m + 2·c``
  exactly one of the two vertices must be chosen; picking ``i_T`` corresponds
  to setting variable *i* to *True* and picking ``i_F`` corresponds to setting
  it to *False*.

* For each clause ``C_j`` (``j`` from 0) create a triangle of three new
  vertices.  A triangle requires at least two of its vertices in any vertex
  cover, so we can leave exactly one vertex uncovered.  The uncovered vertex
  will represent the literal that satisfies the clause.

* Connect each clause‑vertex to the variable‑vertex that makes the literal
  true.  Concretely, if the literal is ``+v`` we add an edge between the clause
  vertex and ``v_T``; if the literal is ``-v`` we connect it to ``v_F``.

With this construction the graph has:

* ``2·m`` vertices for the variables,
* ``3·c`` vertices for the ``c`` clauses,
* ``m`` edges between variable literals,
* ``3·c`` edges inside the clause triangles, and
* ``3·c`` edges linking clause vertices to variable vertices.

The parameter ``k`` is set to ``m + 2·c``.  It is well‑known that the original
3‑SAT formula is satisfiable iff the constructed graph admits a vertex cover
of size at most ``k``.

The ``reduce`` function implements this construction in polynomial time and
returns an instance suitable for the ``VertexCover`` solver.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of literals).

    Returns
    -------
    dict
        A VertexCover instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex indexing
    # Variable vertices: for variable i (1‑based)
    #   true  -> 2*(i-1)
    #   false -> 2*(i-1) + 1
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    base_clause = 2 * m  # first index used for clause vertices

    edges: List[List[int]] = []

    # 1. Variable edges (i_T, i_F)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # 2. Clause triangles and connections
    for j, clause in enumerate(clauses):
        # clause vertices indices
        v0 = base_clause + 3 * j
        v1 = v0 + 1
        v2 = v0 + 2
        clause_vertices = [v0, v1, v2]

        # triangle edges
        edges.append([v0, v1])
        edges.append([v0, v2])
        edges.append([v1, v2])

        # connect each clause vertex to the variable vertex that makes the
        # literal true.
        for k, lit in enumerate(clause):
            var = abs(lit)
            if var == 0:
                # Defensive: literal 0 should never appear, but skip to keep
                # the reduction well‑formed.
                continue
            if lit > 0:
                var_vertex = var_true(var)
            else:
                var_vertex = var_false(var)
            clause_vertex = clause_vertices[k]
            edges.append([clause_vertex, var_vertex])

    total_vertices = base_clause + 3 * c
    k = m + 2 * c

    # Normalise edges (undirected) and remove duplicates.
    normalised = {tuple(sorted(e)) for e in edges}
    edge_list = [list(e) for e in normalised]

    return {"n": total_vertices, "edges": edge_list, "k": k}

