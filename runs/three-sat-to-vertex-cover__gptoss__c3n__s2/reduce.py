"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`ThreeSat` (see ``problems.py``) and the
target problem is :class:`VertexCover`.  The reduction is the classic one
used in many textbooks and matches the description in the NP‑completeness
proof for Vertex Cover.

Construction
=============
* For each variable ``x_i`` (``i`` from ``1`` to ``m``) we create two vertices
  ``v_i_T`` and ``v_i_F`` and add the edge ``[v_i_T, v_i_F]``.  Picking exactly
  one of the two vertices in a vertex cover corresponds to assigning a truth
  value to the variable.
* For each clause ``C_j = (ℓ_1 ∨ ℓ_2 ∨ ℓ_3)`` we create three clause vertices
  ``c_{j,1}``, ``c_{j,2}``, ``c_{j,3}`` and connect them as a triangle (three
  edges).  In any vertex cover at least two vertices of a triangle must be
  chosen.
* Finally we connect each clause vertex to the *negated* literal vertex:
  - If the literal is ``+v`` (i.e. ``x_v`` is true) we connect the clause vertex
    to ``v_v_F`` (the vertex representing ``¬x_v``).
  - If the literal is ``-v`` (i.e. ``¬x_v`` is true) we connect to ``v_v_T``.
  This ensures that if a literal is satisfied (the corresponding *positive*
  vertex is chosen in the cover) the incident edge to the clause vertex is
  already covered, allowing that clause vertex to be the one omitted from the
  triangle.

Parameter ``k``
---------------
The intended size of the vertex cover is ``k = m + 2·|clauses|``:

* ``m`` vertices are needed to cover the ``m`` variable edges (one per variable).
* For each clause we need at least two vertices from its triangle, totalling
  ``2·|clauses|``.

With this ``k`` the source instance is satisfiable iff the constructed graph
has a vertex cover of size at most ``k``.

The implementation below follows exactly this construction and returns a
dictionary conforming to the format required by :class:`VertexCover`.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, VertexCover  # type: ignore  # noqa: F401


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT instance as described in
        ``problems.py`` – it must contain ``"num_vars"`` and ``"clauses"``.

    Returns
    -------
    dict
        A vertex‑cover instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate the source instance – will raise InvalidInstance on error.
    ThreeSat.validate(instance)  # type: ignore[arg-type]

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex numbering:
    #   For variable i (1‑based) we allocate two vertices:
    #       true  -> 2*(i-1)
    #       false -> 2*(i-1) + 1
    #   Clause vertices start after the 2*m variable vertices.
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # 1. Variable edges (forcing a choice per variable).
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # 2. Clause gadgets.
    clause_vertex_start = 2 * m
    for j, clause in enumerate(clauses):
        # Create three vertices for this clause.
        base = clause_vertex_start + 3 * j
        c_vertices = [base, base + 1, base + 2]

        # Triangle edges among the three clause vertices.
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[0], c_vertices[2]])

        # Connect each clause vertex to the negated literal vertex.
        for lit, cv in zip(clause, c_vertices):
            var = abs(lit)
            if lit > 0:
                # literal is x_var, connect to ¬x_var (false vertex)
                edges.append([cv, var_false(var)])
            else:
                # literal is ¬x_var, connect to x_var (true vertex)
                edges.append([cv, var_true(var)])

    n = clause_vertex_start + 3 * len(clauses)
    k = m + 2 * len(clauses)

    # Validate the target instance before returning.
    target_instance = {"n": n, "edges": edges, "k": k}
    VertexCover.validate(target_instance)  # type: ignore[arg-type]
    return target_instance

