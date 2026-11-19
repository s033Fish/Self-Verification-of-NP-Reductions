"""Reduction from 3‑SAT to Vertex Cover.

The source problem is defined by :class:`problems.ThreeSat` and the target
by :class:`problems.VertexCover`.  Both classes are available after importing
``problems``.  The reduction follows the classic construction used in many
complexity textbooks:

* For each variable ``x_i`` we create two vertices ``x_i`` (true) and
  ``¬x_i`` (false) and connect them with an edge.  In any vertex cover we
  must pick at least one of the two vertices, which corresponds to assigning a
  truth value to the variable.
* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we create a triangle of three new
  vertices.  A triangle requires at least two vertices in a vertex cover; the
  third vertex can be left uncovered and will be used to indicate which literal
  satisfies the clause.
* The ``j``‑th vertex of the clause triangle is connected to the literal
  vertex that would make the literal true (the true‑vertex for a positive
  literal, the false‑vertex for a negative literal).

If the formula is satisfiable, we can pick exactly one vertex from each
variable edge (according to the satisfying assignment) and, for each clause,
pick the two clause‑vertices that are **not** linked to the satisfied literal.
This yields a vertex cover of size ``#variables + 2·#clauses``.

Conversely, any vertex cover of that size must contain exactly one vertex
from each variable edge (otherwise we would need more than ``#variables``
vertices) and exactly two vertices from each clause triangle, leaving the
third vertex uncovered.  The uncovered vertex must be adjacent to a literal
vertex that is *not* in the cover, which forces that literal to be true.  This
produces a satisfying assignment.

The ``reduce`` function implements this construction and returns a dictionary
compatible with the Vertex Cover instance format.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes for validation and documentation purposes.
from problems import ThreeSat, VertexCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described in
        the docstring of :class:`problems.ThreeSat`.

    Returns
    -------
    dict
        A Vertex‑Cover instance ``{"n": n, "edges": edges, "k": k}`` such that
        the original formula is satisfiable iff the graph has a vertex cover of
        size at most ``k``.
    """

    # Validate the source instance – this raises InvalidInstance on malformed
    # input, matching the behaviour expected from other reductions.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]  # number of variables
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    edges: List[List[int]] = []

    # Variable vertices: for variable i (0‑based) we use indices 2*i (true) and
    # 2*i+1 (false).  Add the edge representing the exclusive choice.
    for i in range(m):
        vt = 2 * i
        vf = vt + 1
        edges.append([vt, vf])

    # Clause vertices start after the variable vertices.
    base = 2 * m
    for ci, clause in enumerate(clauses):
        # The three vertices of the clause triangle.
        c_vertices = [base + 3 * ci + idx for idx in range(3)]

        # Add the three edges of the triangle.
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])

        # Connect each clause vertex to the literal vertex that would satisfy it.
        for idx, literal in enumerate(clause):
            var_index = abs(literal) - 1  # convert to 0‑based variable index
            if literal > 0:
                lit_vertex = 2 * var_index  # true literal vertex
            else:
                lit_vertex = 2 * var_index + 1  # false literal vertex
            edges.append([c_vertices[idx], lit_vertex])

    n = 2 * m + 3 * num_clauses
    k = m + 2 * num_clauses

    result = {"n": n, "edges": edges, "k": k}
    # Ensure the produced instance conforms to the target specification.
    VertexCover.validate(result)
    return result

