"""Polynomial-time reduction from 3-SAT to Clique.

Standard gadget reduction:

  * For every clause i and every one of its three literals, create a vertex.
    Clause i owns the three vertices 3*i, 3*i+1, 3*i+2.
  * Join two vertices with an edge iff they belong to different clauses and
    their literals are not complementary (i.e. not one the negation of the
    other).  Vertices inside the same clause are never joined.
  * Set k = number of clauses.

A clique of size k must pick exactly one vertex from each clause (no two
vertices of a clause are adjacent) and no two picked literals contradict, so
it yields a satisfying assignment.  Conversely, a satisfying assignment lets
us pick one true literal per clause; those vertices are pairwise adjacent and
form a k-clique.  Thus the graph has a clique of size >= k iff the formula is
satisfiable.

Edge cases:
  * No clauses -> k = 0, and Clique answers yes for k <= 0, matching the
    empty (satisfiable) formula, including num_vars = 0.
  * Duplicate clauses become separate gadgets; the same literal choice can be
    reused because equal literals are adjacent across gadgets.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Clique instance (yes-preserving)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence; clause i owns 3*i .. 3*i+2.
    n = 3 * len(clauses)

    edges = []
    for i in range(len(clauses)):
        for j in range(3):
            u = 3 * i + j
            a = clauses[i][j]
            for i2 in range(i + 1, len(clauses)):
                for j2 in range(3):
                    b = clauses[i2][j2]
                    # Complementary literals cannot both be true.
                    if a != -b:
                        edges.append([u, 3 * i2 + j2])

    return {"n": n, "edges": edges, "k": len(clauses)}
