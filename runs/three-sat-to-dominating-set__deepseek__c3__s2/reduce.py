"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction:
  * For every variable v in 1..m create a "variable gadget": a triangle on
    three new vertices, two standing for the literals +v and -v and one
    auxiliary vertex.
  * For every clause create one "clause vertex" and join it to the three
    variable-gadget vertices of the literals occurring in that clause.
  * Set k = m (the number of variables).

The number of vertices is 3m + (#clauses) and the number of edges is
3m + 3(#clauses), so the reduction is linear time and size.

Correctness sketch:
  (satisfiable => dominating set) Take the m vertices corresponding to a
  satisfying assignment (the true literal of each variable).  Every variable
  gadget is dominated (the chosen vertex dominates the other two triangle
  vertices), and every clause vertex is adjacent to the vertex of a true
  literal, so this is a dominating set of size m.

  (dominating set => satisfiable) Let D be a dominating set with |D| <= m.
  In each variable gadget, the auxiliary vertex is adjacent only to the two
  literal vertices, so if none of the three gadget vertices were in D the
  auxiliary vertex would be undominated.  Hence every gadget contains at
  least one vertex of D, giving |D| >= m; therefore |D| = m, exactly one
  vertex per gadget and no clause vertices.  Since no clause vertex is in D,
  each clause vertex must be adjacent to a chosen literal vertex, so every
  clause contains a literal whose vertex is in D.  Assign each variable the
  truth value that makes its chosen literal true (if the chosen vertex is the
  auxiliary one, choose arbitrarily); every clause is then satisfied by one
  of its chosen literals.
"""


def _literal_vertex(literal: int) -> int:
    """Vertex representing a literal in the variable gadgets."""
    v = abs(literal)
    return 3 * (v - 1) if literal > 0 else 3 * (v - 1) + 1


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    # Variable gadgets: a triangle on {+v, -v, auxiliary}.
    for v in range(1, num_vars + 1):
        a = 3 * (v - 1)
        edges.append([a, a + 1])
        edges.append([a + 1, a + 2])
        edges.append([a, a + 2])

    next_vertex = 3 * num_vars
    for clause in clauses:
        c = next_vertex
        next_vertex += 1
        for literal in clause:
            edges.append([c, _literal_vertex(literal)])

    return {"n": next_vertex, "edges": edges, "k": num_vars}
