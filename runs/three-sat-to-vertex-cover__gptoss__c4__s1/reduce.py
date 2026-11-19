"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`ThreeSat` defined in ``problems.py``.  The
target problem is :class:`VertexCover`.

For a formula with ``m`` variables and ``c`` clauses we construct a graph
with the following gadgets (the classic reduction from Garey & Johnson):

* **Variable gadget** – for each variable ``i`` (1‑based) we create two
  vertices ``v_i_true`` and ``v_i_false`` and add the edge ``(v_i_true,
  v_i_false)``.  In any vertex cover of size ``m`` exactly one endpoint of
  each such edge must be chosen, which corresponds to setting the variable
  to true or false.

* **Clause gadget** – for each clause we create three vertices forming a
  triangle.  The triangle forces the cover to contain at least two of the
  three vertices unless one of them is already covered by the edge to the
  appropriate literal vertex in the variable gadget.

* **Literal edges** – for each literal ``ℓ`` in a clause we connect the
  corresponding clause‑vertex to the literal vertex in the variable gadget:
  ``v_i_true`` for a positive literal ``+i`` and ``v_i_false`` for a
  negative literal ``-i``.

If the formula is satisfiable we can pick for each variable the vertex that
represents the chosen truth value and, for each clause, pick the two clause
vertices whose literals are *not* satisfied; the remaining clause vertex is
adjacent to a selected literal vertex, so the triangle edges are covered.
Thus a vertex cover of size ``m + 2·c`` exists.  Conversely, any vertex cover
of that size yields a satisfying assignment.

The reduction runs in time linear in the size of the formula, i.e. polynomial
time.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, VertexCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the docstring of :class:`ThreeSat`.

    Returns
    -------
    dict
        A Vertex‑Cover instance ``{"n": n, "edges": [...], "k": k}``.

    The function validates the input using :meth:`ThreeSat.validate` and
    constructs the graph exactly as described in the module docstring.
    """

    # Validate the source instance – will raise InvalidInstance on error.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex numbering:
    #   0 .. 2*m-1   – variable vertices (true, false for each variable)
    #   2*m .. 2*m+3*c-1 – clause vertices (three per clause)
    var_true = lambda i: 2 * (i - 1)      # i in 1..m
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # Variable edges (forcing a choice per variable)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Clause vertices and their internal triangle edges
    for ci, clause in enumerate(clauses):
        base = 2 * m + 3 * ci
        c0, c1, c2 = base, base + 1, base + 2
        # triangle
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c2, c0])

        # connect each clause vertex to the appropriate literal vertex
        for lit_idx, literal in enumerate(clause):
            clause_vertex = base + lit_idx
            var = abs(literal)
            if literal > 0:
                literal_vertex = var_true(var)
            else:
                literal_vertex = var_false(var)
            edges.append([clause_vertex, literal_vertex])

    n = 2 * m + 3 * c
    k = m + 2 * c

    # Validate the produced target instance before returning.
    target_instance: Dict[str, Any] = {"n": n, "edges": edges, "k": k}
    VertexCover.validate(target_instance)
    return target_instance

