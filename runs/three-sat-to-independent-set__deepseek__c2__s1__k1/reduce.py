"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (the standard "clause gadget" reduction):

* For every clause occurrence we create a triangle of three vertices, one
  per literal of that clause.  Duplicate clauses each get their own triangle.
* Two vertices in *different* triangles are joined by an edge exactly when
  their literals are complementary (i.e. one is +v and the other is -v).
* Set k = number of clauses.

Why it works:
  An independent set can contain at most one vertex from each triangle, so an
  independent set of size k (the number of clauses) must pick exactly one
  literal from every clause.  The cross edges forbid picking both v and -v,
  so the chosen literals are simultaneously satisfiable, and setting exactly
  those variables accordingly satisfies every clause.  Conversely, any
  satisfying assignment lets us pick one true literal per clause; these
  vertices are pairwise non-adjacent (no two are in the same triangle, and
  no two are complementary), giving an independent set of size k.

Edge cases:
  * No clauses -> n = 0, edges = [], k = 0, and k <= 0 is always yes, matching
    the empty formula being satisfiable.
  * A clause with a repeated variable or both v and -v cannot occur by the
    source validation rules, but the construction still handles it: the
    triangle would collapse / add an edge and the reduction remains a valid
    (if not size-preserving) mapping.  We keep every literal as its own
    vertex regardless.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance.

    instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    returns:  {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Vertex 3*c + j corresponds to literal clauses[c][j].
    n = 3 * num_clauses

    edges = []
    edge_set = set()

    def add_edge(u, v):
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in edge_set:
            edge_set.add((a, b))
            edges.append([a, b])

    # Triangle inside every clause gadget.
    for c in range(num_clauses):
        base = 3 * c
        add_edge(base, base + 1)
        add_edge(base, base + 2)
        add_edge(base + 1, base + 2)

    # Edges between complementary literals in different clauses.
    for c in range(num_clauses):
        for j in range(3):
            literal = clauses[c][j]
            u = 3 * c + j
            for d in range(c + 1, num_clauses):
                for i in range(3):
                    if clauses[d][i] == -literal:
                        v = 3 * d + i
                        add_edge(u, v)

    return {"n": n, "edges": edges, "k": num_clauses}
