"""Polynomial-time reduction from 3-SAT to Clique.

Standard construction:
  * For every clause and every literal position in it, create one vertex.
    Vertices are grouped by clause: vertex 3*c + p corresponds to the p-th
    literal of clause c.
  * Add an edge between two vertices from different clauses exactly when
    their literals are not complementary (i.e. not v and -v).  Vertices in
    the same clause are never adjacent.
  * Set k = number of clauses.

A clique of size k must pick exactly one vertex from each of the k clauses,
and pairwise non-complementarity means the chosen literals can all be made
true simultaneously, yielding a satisfying assignment.  Conversely, any
satisfying assignment gives one true literal per clause, and those vertices
are pairwise adjacent.  A formula with no clauses maps to k = 0, which the
Clique problem answers yes, matching the empty 3-SAT formula.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges = []

    # literal of vertex 3*c + p
    def literal(c, p):
        return clauses[c][p]

    for c1 in range(len(clauses)):
        for c2 in range(c1 + 1, len(clauses)):
            for p1 in range(3):
                l1 = literal(c1, p1)
                for p2 in range(3):
                    l2 = literal(c2, p2)
                    # Complementary literals cannot both be true.
                    if l1 != -l2:
                        edges.append([3 * c1 + p1, 3 * c2 + p2])

    return {"n": n, "edges": edges, "k": len(clauses)}
