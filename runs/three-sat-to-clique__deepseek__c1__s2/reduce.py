"""Polynomial-time reduction from 3-SAT (ThreeSat) to Clique.

Gadget construction (standard):
  * For every clause and every one of its three literals, create one vertex.
    Vertices are numbered 0..3*C-1, where C is the number of clauses.
  * Two vertices are joined by an edge iff they come from different clauses
    and their literals are not complementary (i.e. not v and -v).
  * Set k = C, the number of clauses.

Correctness:
  (=>) A satisfying assignment makes at least one literal true in each
       clause. Pick one true literal per clause; these C vertices lie in
       pairwise different clauses and no two are complementary (a variable
       cannot be both true and false), so they form a clique of size C.
  (<=) A clique of size C must contain at most one vertex per clause (no
       edges inside a clause) and there are exactly C clauses, hence exactly
       one vertex per clause. Since no two chosen literals are complementary,
       the assignment that sets each chosen literal true (and all other
       variables arbitrarily, e.g. false) is consistent and satisfies every
       clause. Thus a clique of size >= C exists iff the formula is
       satisfiable.

Edge case: a formula with no clauses is satisfiable. The reduction then
returns n = 0, edges = [], k = 0, and k <= 0 is always a yes-instance of
Clique, matching the source answer.

The construction uses O(C) vertices and O(C^2) edges, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    """Reduce a ThreeSat instance to a Clique instance."""
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # No clauses: satisfiable. Return the empty graph with k = 0 (always yes).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # One vertex per literal occurrence. vertex_literal[i] is the signed
    # literal represented by vertex i; vertex_clause[i] is its clause index.
    vertex_literal = []
    vertex_clause = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_literal.append(int(lit))
            vertex_clause.append(ci)

    n = len(vertex_literal)

    edges = []
    for i in range(n):
        li = vertex_literal[i]
        ci = vertex_clause[i]
        for j in range(i + 1, n):
            # No edge within the same clause: a clique takes at most one
            # literal per clause.
            if ci == vertex_clause[j]:
                continue
            # No edge between complementary literals.
            if li == -vertex_literal[j]:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": num_clauses}
