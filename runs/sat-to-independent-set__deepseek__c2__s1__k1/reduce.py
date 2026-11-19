"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (the classic clause/literal gadget):

  * For every literal occurrence in every clause, create one vertex.  So the
    total number of vertices n is the total number of literal occurrences.
  * For each clause, put all of its vertices into a clique.  This forces an
    independent set to choose at most one literal per clause.
  * For every variable v, connect every vertex labelled +v with every vertex
    labelled -v (in any clauses).  This forbids choosing contradictory
    literals.
  * Set k = number of clauses.

Correctness:
  * If the formula is satisfiable, pick, in each clause, one literal that is
    true under a satisfying assignment.  These k vertices are pairwise
    non-adjacent: no two come from the same clause (so no clique edge) and no
    two are contradictory (both are true).  Hence an independent set of size k.
  * If the graph has an independent set of size k, it contains exactly one
    vertex per clause (at most one per clause, and there are k clauses).  The
    chosen literals are pairwise non-contradictory, so the assignment that
    makes them all true is consistent and satisfies every clause.

Edge cases:
  * No clauses -> n = 0, k = 0, and k <= 0 is yes, matching satisfiability.
  * An empty clause contributes no vertices, so at most k-1 vertices can be
    chosen; the target is no, matching the unsatisfiable source.
  * Repeated literals / repeated clauses / tautological clauses are handled
    naturally by the occurrence-based construction.
"""


def reduce(instance):
    """Map a SAT instance to an Independent Set instance.

    Input:  {"num_vars": m, "clauses": [[literal, ...], ...]}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]

    edges = set()

    # Assign one vertex per literal occurrence, recording each clause's vertices.
    next_vertex = 0
    clause_vertices = []
    for clause in clauses:
        vertices = []
        for _literal in clause:
            vertices.append(next_vertex)
            next_vertex += 1
        clause_vertices.append(vertices)

        # Clique among the vertices of this clause.
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                a, b = vertices[i], vertices[j]
                edges.add((a, b) if a < b else (b, a))

    # Group vertices by the literal they represent, then connect opposites.
    literal_vertices = {}
    for clause, vertices in zip(clauses, clause_vertices):
        for literal, vertex in zip(clause, vertices):
            literal_vertices.setdefault(literal, []).append(vertex)

    for literal, vertices in literal_vertices.items():
        opposite = literal_vertices.get(-literal)
        if opposite is None:
            continue
        for a in vertices:
            for b in opposite:
                edges.add((a, b) if a < b else (b, a))

    n = next_vertex
    k = len(clauses)
    return {
        "n": n,
        "edges": [list(edge) for edge in sorted(edges)],
        "k": k,
    }
