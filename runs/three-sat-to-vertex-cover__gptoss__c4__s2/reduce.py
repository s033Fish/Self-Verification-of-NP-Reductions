"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`problems.ThreeSat` and the target is
``problems.VertexCover``.  The reduction follows the classic textbook
construction (see e.g. Garey & Johnson, *Computers and Intractability*,
Section 3.1).  For a formula with ``m`` variables and ``c`` clauses we build
an undirected graph with:

* ``2*m`` vertices representing the two possible truth assignments for each
  variable.  For variable ``i`` (1‑based) we use the vertices ``2*(i-1)`` for
  *true* and ``2*(i-1)+1`` for *false*.  An edge between them forces a vertex
  cover to pick at least one of the two – this encodes the choice of a truth
  value.
* For each clause we add three new vertices forming a triangle.  The three
  vertices correspond to the three literals of the clause.
* For each literal ``ℓ`` in a clause we connect the clause‑vertex that
  represents ``ℓ`` to the *opposite* literal‑vertex of the variable.  If the
  literal is ``+v`` we connect to the *false* vertex of ``v``; if the literal
  is ``‑v`` we connect to the *true* vertex of ``v``.

The parameter ``k`` of the Vertex‑Cover instance is set to ``m + 2*c``.  It is
well‑known that the formula is satisfiable iff the constructed graph has a
vertex cover of size at most ``k``.

The implementation below validates the input using the problem classes from
``problems.py`` and then returns a dictionary that conforms to the Vertex‑Cover
instance format.
"""

from __future__ import annotations

from typing import Dict, List

import problems


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary following the format of :class:`problems.ThreeSat` –
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        A Vertex‑Cover instance ``{"n": n, "edges": [...], "k": k}`` such
        that the original formula is satisfiable iff the graph has a vertex
        cover of size at most ``k``.
    """

    # Validate the source instance – will raise InvalidInstance on error.
    problems.ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex ids for variable assignments
    # true vertex = 2*(i-1), false vertex = 2*(i-1)+1 for variable i (1‑based)
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # 1. Variable edges (force a choice of true/false)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # 2. Clause vertices and edges
    # Clause vertices start after the 2*m variable vertices
    clause_base_offset = 2 * m
    for clause_idx, clause in enumerate(clauses):
        # three vertices for this clause
        base = clause_base_offset + 3 * clause_idx
        c_vertices = [base, base + 1, base + 2]

        # triangle edges among the three clause vertices
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[0], c_vertices[2]])

        # connect each clause vertex to the *negation* vertex of its literal
        for pos, literal in enumerate(clause):
            var = abs(literal)
            # literal > 0 means the clause is satisfied by the true assignment
            # of the variable, so we connect to the *false* vertex.
            if literal > 0:
                opposite = var_false(var)
            else:
                opposite = var_true(var)
            edges.append([c_vertices[pos], opposite])

    n = 2 * m + 3 * c
    k = m + 2 * c

    target_instance = {"n": n, "edges": edges, "k": k}

    # Validate the constructed target instance.
    problems.VertexCover.validate(target_instance)
    return target_instance

