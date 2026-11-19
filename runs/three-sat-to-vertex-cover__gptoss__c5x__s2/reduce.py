"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`ThreeSat` (see ``problems.py``) and the
target problem is :class:`VertexCover`.

For a formula with ``m`` variables and ``c`` clauses we construct a graph
with the following vertices and edges (the classic reduction due to
Karp):

* **Variable vertices** – for each variable ``x_i`` we create two vertices
  ``v_{i,True}`` and ``v_{i,False}``.  An edge between them forces a vertex
  cover to pick at least one of the two, which corresponds to assigning the
  variable either true or false.
* **Clause vertices** – for each clause we create a triangle of three
  vertices, one for each literal.  A triangle needs at least two vertices in
  any vertex cover, so exactly one literal may remain uncovered – the literal
  that is satisfied.
* **Literal‑to‑variable edges** – each clause‑vertex is connected to the
  variable‑vertex that makes the literal true (e.g. a positive literal ``x``
  connects to ``v_{x,True}``, a negative literal ``¬x`` connects to
  ``v_{x,False}``).

The required cover size is ``k = m + 2 * c`` because we must pick one vertex
from each variable edge (``m`` vertices) and at least two vertices from each
clause triangle (``2*c`` vertices).

The ``reduce`` function validates the input, builds the graph as described
above and returns an instance compatible with ``VertexCover.validate``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, VertexCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as defined by
        :class:`ThreeSat`.

    Returns
    -------
    dict
        A vertex‑cover instance ``{"n": ..., "edges": ..., "k": ...}``.
    """

    # Validate the source instance – will raise InvalidInstance on error.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex indexing:
    #   variable true  = 2*i
    #   variable false = 2*i + 1   for i in 0..m-1
    #   clause vertices start after 2*m and are laid out consecutively
    #   (three per clause).
    var_true = lambda i: 2 * i
    var_false = lambda i: 2 * i + 1
    clause_base = 2 * m

    edges: List[List[int]] = []

    # 1. Variable edges (force a choice per variable)
    for i in range(m):
        edges.append([var_true(i), var_false(i)])

    # 2. Clause gadgets
    for ci, clause in enumerate(clauses):
        # vertices for this clause
        v0 = clause_base + ci * 3 + 0
        v1 = clause_base + ci * 3 + 1
        v2 = clause_base + ci * 3 + 2
        # triangle edges
        edges.append([v0, v1])
        edges.append([v1, v2])
        edges.append([v0, v2])
        # literal‑to‑variable edges
        for idx, lit in enumerate(clause):
            var = abs(lit) - 1  # variables are 1‑based in the input
            clause_vertex = clause_base + ci * 3 + idx
            if lit > 0:
                edges.append([clause_vertex, var_true(var)])
            else:
                edges.append([clause_vertex, var_false(var)])

    n = 2 * m + 3 * c
    k = m + 2 * c

    result = {"n": n, "edges": edges, "k": k}
    # Validate the produced target instance before returning.
    VertexCover.validate(result)
    return result

