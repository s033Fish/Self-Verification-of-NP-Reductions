"""Reduction from 3‑SAT to Vertex Cover.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  The target
problem is ``VertexCover`` with the format ``{"n": n, "edges": [[u, v], ...],
"k": k}``.

We implement the classic polynomial‑time reduction:

* For each variable ``v`` (1‑based) we create two vertices ``v_pos`` and
  ``v_neg`` and add the edge ``(v_pos, v_neg)``.  In any vertex cover of size
  ``m + 2·c`` exactly one endpoint of this edge must be chosen – this encodes a
  truth assignment for the variable.

* For each clause ``C_i`` we create three new vertices forming a triangle.  A
  triangle needs at least two vertices in a vertex cover, therefore with the
  budget ``2·c`` we are forced to pick exactly two of them.  The remaining (the
  third) vertex corresponds to the literal that satisfies the clause.

* Finally we connect each clause‑literal vertex to the appropriate variable
  vertex: a positive literal ``+v`` is connected to ``v_pos`` and a negative
  literal ``-v`` to ``v_neg``.  This forces the cover to include the literal
  vertex only when the opposite variable vertex is already chosen, mirroring
  the logical condition that a clause is satisfied when at least one literal
  is true.

With ``m`` variables and ``c`` clauses the constructed graph has
``n = 2·m + 3·c`` vertices and the parameter ``k = m + 2·c``.  It can be shown
that the 3‑SAT instance is satisfiable iff the resulting graph has a vertex
cover of size at most ``k``.

The ``reduce`` function performs this construction in polynomial time and
returns a dictionary compatible with the ``VertexCover`` specification.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of ints).  The format follows the docstring of the
        ``ThreeSat`` class in ``problems.py``.

    Returns
    -------
    dict
        A vertex‑cover instance ``{"n": n, "edges": edges, "k": k}``.
    """

    # Extract data from the 3‑SAT instance.
    m: int = instance["num_vars"]  # number of variables
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)  # number of clauses

    # Helper functions to map a variable to its two vertices.
    #   Positive literal vertex index: 2*(v-1)
    #   Negative literal vertex index: 2*(v-1) + 1
    var_pos = lambda v: 2 * (v - 1)
    var_neg = lambda v: 2 * (v - 1) + 1

    edges: List[List[int]] = []

    # 1. Variable edges (v_pos, v_neg) for each variable.
    for v in range(1, m + 1):
        edges.append([var_pos(v), var_neg(v)])

    # 2. Clause triangles and connections to variable literals.
    for i, clause in enumerate(clauses):
        # Base index for the three vertices of this clause.
        base = 2 * m + 3 * i
        a, b, c_idx = base, base + 1, base + 2
        # Triangle edges among the three clause vertices.
        edges.append([a, b])
        edges.append([b, c_idx])
        edges.append([c_idx, a])

        # Connect each clause literal vertex to the appropriate variable vertex.
        for offset, literal in enumerate(clause):
            lit_vertex = base + offset
            var = abs(literal)
            if literal > 0:
                # Positive literal connects to the positive variable vertex.
                edges.append([lit_vertex, var_pos(var)])
            else:
                # Negative literal connects to the negative variable vertex.
                edges.append([lit_vertex, var_neg(var)])

    n = 2 * m + 3 * c
    k = m + 2 * c

    return {"n": n, "edges": edges, "k": k}

