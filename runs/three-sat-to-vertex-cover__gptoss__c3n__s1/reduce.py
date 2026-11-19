"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`problems.ThreeSat` and the target problem is
``problems.VertexCover``.  Both classes only provide a ``validate`` method –
no solvers are supplied.  This file implements ``reduce`` which maps a 3‑SAT
instance to a vertex‑cover instance such that the latter has a cover of size
``k`` *iff* the former formula is satisfiable.

The classic reduction works as follows (see any textbook on NP‑completeness):

* For each variable ``x_i`` (``i`` from ``1`` to ``m``) create two vertices
  ``v_{i,true}`` and ``v_{i,false}`` and add an edge between them.  Selecting
  exactly one of the two vertices will represent the truth value of the
  variable.
* For each clause ``C_j`` create a triangle of three vertices, one for each
  literal in the clause.  The three edges of the triangle force the cover to
  contain at least two of the three vertices.
* Connect each clause‑literal vertex to the *true* vertex of the variable if
  the literal is positive, otherwise connect it to the *false* vertex.  This
  guarantees that the single clause‑literal vertex that can be omitted from
  the cover corresponds to a literal that is satisfied by the chosen truth
  assignment.

If there are ``m`` variables and ``c`` clauses, the construction yields

``n = 2*m + 3*c`` vertices and the parameter ``k = m + 2*c``.  A vertex cover of
size at most ``k`` exists exactly when the original formula is satisfiable.

The function below follows this construction and returns a dictionary that
conforms to the format expected by :class:`problems.VertexCover`.  It also
validates the output using the problem's ``validate`` method to catch any
programming errors early.
"""

from __future__ import annotations

from typing import Dict, List

import problems


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined in
        :class:`problems.ThreeSat`.

    Returns
    -------
    dict
        An instance of the target problem (Vertex Cover) with keys ``"n"``,
        ``"edges"`` and ``"k"``.
    """
    # Validate the source instance first – this will raise if the input is
    # malformed.
    problems.ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex numbering:
    #   0 .. 2*m-1          – variable vertices (true, false pairs)
    #   2*m .. 2*m+3*c-1   – clause‑literal vertices (three per clause)
    var_true: List[int] = []   # index of the true vertex for each variable
    var_false: List[int] = []  # index of the false vertex for each variable
    for i in range(m):
        var_true.append(2 * i)
        var_false.append(2 * i + 1)

    base_clause = 2 * m
    edges: List[List[int]] = []

    # 1. Variable edges (force picking at least one of true/false)
    for i in range(m):
        edges.append([var_true[i], var_false[i]])

    # 2. Clause triangles and connections to variable vertices
    for ci, clause in enumerate(clauses):
        # vertices for the three literals of this clause
        lit_vertices = [base_clause + ci * 3 + offset for offset in range(3)]

        # a) triangle edges
        a, b, d = lit_vertices
        edges.append([a, b])
        edges.append([b, d])
        edges.append([a, d])

        # b) connect each literal vertex to the appropriate variable vertex
        for lit, v in zip(clause, lit_vertices):
            var = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                # positive literal connects to the true vertex of the variable
                edges.append([v, var_true[var]])
            else:
                # negative literal connects to the false vertex
                edges.append([v, var_false[var]])

    n = 2 * m + 3 * c
    k = m + 2 * c

    vc_instance: Dict = {"n": n, "edges": edges, "k": k}
    # Ensure the produced instance is well‑formed.
    problems.VertexCover.validate(vc_instance)
    return vc_instance

