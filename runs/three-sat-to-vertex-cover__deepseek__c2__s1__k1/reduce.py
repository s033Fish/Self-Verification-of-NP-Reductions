"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction
------------
Given a 3-SAT instance with m variables and C clauses:

* For each variable v in 1..m create two vertices, one for the positive
  literal +v and one for the negative literal -v, joined by an edge.  Any
  vertex cover must contain at least one endpoint of this edge, so at least
  one vertex per variable is chosen.

* For each clause create a triangle on three new vertices, one per literal.
  Any vertex cover must contain at least two of the three triangle vertices.

* Join each clause-literal vertex to the variable vertex of that literal.

Set k = m + 2*C.

Correctness
-----------
(=>) From a satisfying assignment, pick for each variable the vertex of the
true literal (m vertices), and for each clause pick the two triangle vertices
whose literals are false (the third literal is true, so its cross edge is
already covered).  This is a vertex cover of size m + 2*C.

(<=) A cover of size m + 2*C must pick exactly one vertex per variable gadget
(at least one, and the budget forces exactly one after paying two per clause)
and exactly two per clause triangle.  The unpicked triangle vertex corresponds
to a literal whose cross edge must be covered by the chosen variable vertex,
so that literal is set true; this satisfies every clause.

Edge cases
----------
* No clauses: the graph is just m disjoint edges, k = m, and the empty
  assignment (or any assignment) is a cover, matching satisfiability.
* m = 0 with no clauses: n = 0, edges = [], k = 0, which is a yes instance.
"""


def reduce(instance):
    """Return a Vertex Cover instance equivalent to the given 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadgets: vertices 2*(v-1) and 2*(v-1)+1 for variable v.
    for v in range(1, num_vars + 1):
        pos = 2 * (v - 1)
        neg = pos + 1
        edges.append([pos, neg])

    # Clause gadgets: a triangle per clause, plus cross edges.
    next_vertex = 2 * num_vars
    for clause in clauses:
        base = next_vertex
        next_vertex += 3
        # Triangle on the three literal vertices.
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base + 2, base])
        # Cross edges to the corresponding variable vertices.
        for offset, literal in enumerate(clause):
            var = abs(literal)
            if literal > 0:
                target = 2 * (var - 1)
            else:
                target = 2 * (var - 1) + 1
            edges.append([base + offset, target])

    k = num_vars + 2 * len(clauses)
    return {"n": next_vertex, "edges": edges, "k": k}
