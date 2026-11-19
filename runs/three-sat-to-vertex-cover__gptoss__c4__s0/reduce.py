"""Reduction from 3-SAT to Vertex Cover.

The reduction follows the classic construction:

* For each variable x_i we create two vertices ``v_i`` (true) and ``¬v_i``
  (false) and connect them with an edge. Selecting exactly one of the two
  vertices in a vertex cover corresponds to fixing the truth value of the
  variable.
* For each clause C = (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) we create a triangle of three vertices,
  one for each literal. The triangle forces the vertex cover to contain at
  least two of the three clause vertices; the remaining (potentially uncovered)
  vertex can be left out only if the corresponding literal is satisfied.
* Finally we connect each clause‑literal vertex to the variable vertex that
  represents the same literal (true vertex for a positive literal, false
  vertex for a negative literal). This ensures that if a literal is chosen
  to be the uncovered vertex of its clause, the corresponding variable vertex
  must be taken into the cover, i.e., the literal must be true.

If the formula has *m* variables and *c* clauses, the constructed graph has
``n = 2*m + 3*c`` vertices.  A vertex cover of size ``k = m + 2*c`` exists
iff the original formula is satisfiable: we must pick exactly one vertex from
each variable edge (m vertices) and at least two vertices from each clause
triangle (2*c vertices).  This is the standard reduction.

The implementation below builds this graph and returns the appropriate
instance dictionary for the ``VertexCover`` problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, VertexCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    The input ``instance`` is assumed to be a valid 3‑SAT instance as defined
    by :class:`ThreeSat`. The function returns a dictionary that conforms to
    the format required by :class:`VertexCover`.
    """
    # Validate the source instance (will raise if malformed).
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex indexing scheme:
    #   0 .. 2*m-1   : variable vertices (true_i, false_i)
    #   2*m .. ...   : clause literal vertices (three per clause)
    def var_true(v: int) -> int:
        return 2 * (v - 1)

    def var_false(v: int) -> int:
        return 2 * (v - 1) + 1

    edges: List[List[int]] = []

    # 1. Variable edges (true_i -- false_i)
    for v in range(1, m + 1):
        edges.append([var_true(v), var_false(v)])

    # 2. Clause vertices and edges.
    clause_vertex_start = 2 * m
    for ci, clause in enumerate(clauses):
        # three vertices for this clause
        base = clause_vertex_start + 3 * ci
        v1, v2, v3 = base, base + 1, base + 2
        # triangle among clause vertices
        edges.append([v1, v2])
        edges.append([v2, v3])
        edges.append([v3, v1])
        # connect each clause literal vertex to the appropriate variable vertex
        for pos, lit in enumerate(clause):
            var = abs(lit)
            clause_vertex = base + pos
            if lit > 0:
                edges.append([clause_vertex, var_true(var)])
            else:
                edges.append([clause_vertex, var_false(var)])

    n = 2 * m + 3 * c
    k = m + 2 * c

    vc_instance = {"n": n, "edges": edges, "k": k}
    VertexCover.validate(vc_instance)
    return vc_instance

