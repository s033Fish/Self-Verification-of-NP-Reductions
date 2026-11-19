"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`problems.ThreeSat` and the target is
``VertexCover``.  The classic polynomial‑time reduction builds a graph that
forces a vertex cover of size ``m + 2·c`` (where ``m`` is the number of
variables and ``c`` the number of clauses) exactly when the formula is
satisfiable.

Construction details
---------------------
* For each variable ``i`` (1‑based) we create two vertices ``v_i`` and
  ``¬v_i`` and add the edge ``[v_i, ¬v_i]``.  In any vertex cover of size
  ``≤ m + 2·c`` at least one endpoint of this edge must be chosen – this
  corresponds to fixing a truth value for the variable.
* For each clause we create a triangle of three new vertices ``c_{j,0}``,
  ``c_{j,1}``, ``c_{j,2}``.  Covering all three edges of a triangle needs at
  least two of its vertices, so any optimal cover will contain exactly two of
  them.
* Finally, for each literal of a clause we connect the corresponding clause
  vertex to the literal vertex representing that literal.  If a literal is
  true under the chosen assignment, its vertex is already in the cover and we
  can leave the connected clause vertex uncovered; the uncovered vertex tells
  us which literal satisfied the clause.

The resulting graph has ``n = 2·m + 3·c`` vertices and the parameter ``k`` is
``m + 2·c``.  The reduction runs in time linear in the size of the input.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for validation; the reduction must not call
# any solver methods.
from problems import ThreeSat, VertexCover  # noqa: F401


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑literal lists) as defined by :class:`ThreeSat`.

    Returns
    -------
    dict
        A vertex‑cover instance ``{"n": n, "edges": edges, "k": k}`` that
        satisfies the correctness condition described in the module docstring.
    """
    # Validate the source instance; this raises InvalidInstance if malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex numbering:
    #   0 .. 2*m-1   – literal vertices (true, false) for each variable.
    #   2*m .. 2*m+3*c-1 – clause‑triangle vertices.
    def true_vertex(var: int) -> int:
        return 2 * (var - 1)

    def false_vertex(var: int) -> int:
        return 2 * (var - 1) + 1

    n = 2 * m + 3 * c
    edges: List[List[int]] = []

    # 1. Variable edges (v_i, ¬v_i).
    for var in range(1, m + 1):
        edges.append([true_vertex(var), false_vertex(var)])

    # 2. Clause triangles and literal connections.
    for idx, clause in enumerate(clauses):
        base = 2 * m + 3 * idx  # first vertex of this clause's triangle
        # Triangle edges among the three clause vertices.
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])
        # Connect each clause vertex to the corresponding literal vertex.
        for pos, lit in enumerate(clause):
            var = abs(lit)
            lit_vertex = true_vertex(var) if lit > 0 else false_vertex(var)
            edges.append([base + pos, lit_vertex])

    k = m + 2 * c
    return {"n": n, "edges": edges, "k": k}

