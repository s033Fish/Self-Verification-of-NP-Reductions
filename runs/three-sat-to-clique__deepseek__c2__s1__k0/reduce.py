"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Construction
------------
For a 3-SAT instance with clauses C_0, ..., C_{k-1} (k = number of clauses),
create 3 vertices for each clause, one per literal occurrence.  Two vertices
are joined by an edge exactly when they come from *different* clauses and
their literals are not complementary (i.e. not l and -l).

A clique of size k must pick exactly one vertex from each clause triangle
(there are k triangles and no edges inside a triangle), and the chosen
literals are pairwise non-contradictory, so they can be extended to a
satisfying assignment.  Conversely, any satisfying assignment supplies one
true literal per clause; those vertices form a k-clique.

Special case: if there are no clauses, k = 0 and the target graph has n = 0
vertices, which Clique answers yes for (k <= 0), matching the empty 3-SAT
formula being satisfiable.
"""

from itertools import combinations


def reduce(instance):
    """Return a Clique instance that is yes iff the 3-SAT instance is yes."""
    clauses = instance["clauses"]
    k = len(clauses)

    # Vertex i*3 + j corresponds to literal j of clause i.
    n = 3 * k
    edges = []

    # Connect compatible literals belonging to different clauses.
    for i, j in combinations(range(k), 2):
        for a in range(3):
            lit_a = clauses[i][a]
            for b in range(3):
                lit_b = clauses[j][b]
                # Complementary literals cannot both be true.
                if lit_a != -lit_b:
                    u = 3 * i + a
                    v = 3 * j + b
                    edges.append([u, v])

    return {"n": n, "edges": edges, "k": k}
