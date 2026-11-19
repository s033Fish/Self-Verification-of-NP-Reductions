"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Given a CNF formula with clauses C_1, ..., C_m, build a graph G as follows:

  * For every literal occurrence in every clause, create one vertex.  A vertex
    is labelled by the pair (clause index, literal).
  * Join two vertices with an edge iff they come from *different* clauses and
    their literals are not complementary (i.e. not both v and -v).
  * Set k = number of clauses m.

Correctness:
  * (SAT => Clique) If an assignment satisfies every clause, choose one true
    literal per clause.  The chosen vertices lie in distinct clauses and no two
    are complementary (both would be true), so they form a clique of size m.
  * (Clique => SAT) A clique of size m must contain exactly one vertex from
    each clause (vertices of the same clause are never adjacent).  No two
    chosen literals are complementary, so setting each chosen literal true
    yields a consistent assignment that satisfies every clause.

Edge cases:
  * No clauses: m = 0, so k = 0 and the target is yes (k <= 0 always yes).
  * An empty clause contributes no vertices, so the graph cannot contain a
    clique of size m and the target is no, as required.

The construction is polynomial: O(V^2) edges for V literal occurrences.
"""


def reduce(instance):
    """Map a SAT instance to a Clique instance with the same answer."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence, remembering its clause.
    vertices = []  # list of (clause_index, literal)
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((clause_index, literal))

    n = len(vertices)
    edges = []
    for i in range(n):
        clause_i, literal_i = vertices[i]
        for j in range(i + 1, n):
            clause_j, literal_j = vertices[j]
            # Different clauses and not a contradictory pair.
            if clause_i != clause_j and literal_i != -literal_j:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}
