"""Reduction from 3-SAT to Vertex Cover.

The source problem is :class:`ThreeSat` (defined in ``problems.py``) and the
target problem is :class:`VertexCover`.  The reduction follows the classic
polynomial‑time construction used in many textbooks:

* For each variable ``x_i`` we create two vertices ``x_i`` (true) and ``¬x_i``
  (false) and add an edge between them.  In any vertex cover of size ``k`` at
  least one endpoint of this edge must be chosen, which corresponds to fixing
  a truth value for the variable.

* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we create three new vertices forming a
  triangle.  A triangle needs at least two vertices in a vertex cover, so the
  uncovered vertex can be interpreted as the literal that satisfies the clause.
  Each of the three clause vertices is connected to the vertex representing
  the literal that would make the clause true.

If the original formula has ``m`` variables and ``c`` clauses, the constructed
graph has ``2*m + 3*c`` vertices and the parameter ``k`` is set to ``m + 2*c``.
It is well‑known that the formula is satisfiable iff the graph has a vertex
cover of size at most ``k``.

The ``reduce`` function validates the input using ``ThreeSat.validate`` and
returns an instance of the target problem that respects the format required
by ``VertexCover.validate``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, VertexCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``VertexCover`` format such that the
        answer to the returned instance is *yes* exactly when the answer to
        the input instance is *yes*.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex numbering:
    #   0 .. 2*m-1   – variable vertices (true, false pairs)
    #   2*m .. 2*m+3*c-1 – clause gadget vertices (three per clause)
    var_true = lambda var: 2 * (var - 1)          # var in 1..m
    var_false = lambda var: 2 * (var - 1) + 1

    n = 2 * m + 3 * c
    edges: List[List[int]] = []

    # 1. Variable edges (x_i, ¬x_i)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # 2. Clause gadgets
    for idx, clause in enumerate(clauses):
        base = 2 * m + 3 * idx  # first vertex of this clause's triangle
        # a) triangle edges among the three clause vertices
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])
        # b) connect each clause vertex to the corresponding literal vertex
        for pos, literal in enumerate(clause):
            lit_vertex = var_true(literal) if literal > 0 else var_false(-literal)
            clause_vertex = base + pos
            edges.append([clause_vertex, lit_vertex])

    k = m + 2 * c

    vc_instance: Dict = {"n": n, "edges": edges, "k": k}
    # Validate the constructed target instance before returning.
    VertexCover.validate(vc_instance)
    return vc_instance

