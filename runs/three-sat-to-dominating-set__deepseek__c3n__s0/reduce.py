"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
Let the 3-SAT instance have m variables and c clauses.

Variable gadgets: for each variable v (1..m) add two vertices
    T(v) = 2*(v-1)      (represents the literal  +v)
    F(v) = 2*(v-1) + 1  (represents the literal  -v)
joined by an edge.  The two endpoints of this edge are adjacent only to
each other, so every dominating set must contain at least one of them.

Clause gadgets: for each clause j add one new vertex C(j) and connect it
to the three variable-gadget vertices representing its three literals.

Budget: k = m.

Correctness
-----------
* If the formula is satisfiable, take the vertex of each variable's true
  literal (m vertices).  Every variable edge is dominated (one endpoint is
  chosen, the other is its neighbour) and every clause vertex is dominated
  because the clause contains a true literal whose vertex was chosen.
  Hence the graph has a dominating set of size m = k.

* Conversely let D be a dominating set with |D| <= m.  Since the endpoints
  of each variable edge are adjacent only to each other, D must contain at
  least one endpoint of each of the m variable edges, so |D| = m and D
  contains exactly one endpoint per variable and no clause vertex.  Every
  clause vertex must therefore be dominated by one of the chosen literal
  vertices, i.e. every clause contains a literal whose variable was set to
  make that literal true.  Setting variable v true iff T(v) in D thus
  satisfies every clause, so the formula is satisfiable.

Hence the answer is yes for the 3-SAT instance exactly when it is yes for
the constructed Dominating Set instance.  The construction has O(m + c)
vertices and edges and runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a Dominating Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    def literal_vertex(literal: int) -> int:
        v = abs(literal)
        base = 2 * (v - 1)
        return base if literal > 0 else base + 1

    edges: list[list[int]] = []

    # Variable gadgets: an edge between the true and false literal vertex.
    for v in range(1, num_vars + 1):
        t = 2 * (v - 1)
        f = t + 1
        edges.append([t, f])

    n = 2 * num_vars
    # Clause gadgets: one vertex adjacent to the three literal vertices.
    for clause in clauses:
        c = n
        n += 1
        for literal in clause:
            edges.append([c, literal_vertex(literal)])

    k = num_vars
    return {"n": n, "edges": edges, "k": k}
