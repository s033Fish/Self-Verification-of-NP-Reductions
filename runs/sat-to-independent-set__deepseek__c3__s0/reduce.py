"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (standard):
  * For every clause, create one vertex per literal occurrence.  All vertices
    belonging to the same clause are pairwise connected (a clique), so an
    independent set can pick at most one literal from each clause.
  * For every variable v, connect every vertex labelled +v with every vertex
    labelled -v, so an independent set cannot pick both v and its negation.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by picking
one true literal per clause.  Conversely an independent set of size >= k must
pick exactly one vertex from each clause clique (there are k disjoint cliques,
so at most k vertices are selectable), and the absence of complementary edges
lets us turn those choices into a satisfying assignment.

Edge cases:
  * No clauses -> k = 0 -> target answers yes (always true).
  * An empty clause contributes no vertices but raises k, so no independent set
    of size k exists -> target answers no, matching SAT.
"""


def reduce(instance):
    """Map a SAT instance {"num_vars", "clauses"} to an Independent Set
    instance {"n", "edges", "k"} with the same yes/no answer."""
    clauses = instance["clauses"]

    # vertex id -> literal it represents
    literal_of = []
    # clause index -> list of vertex ids created for it
    clause_vertices = []

    for clause in clauses:
        verts = []
        for literal in clause:
            verts.append(len(literal_of))
            literal_of.append(literal)
        clause_vertices.append(verts)

    edges = set()

    # Clique edges inside each clause: at most one literal per clause.
    for verts in clause_vertices:
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                u, v = verts[i], verts[j]
                edges.add((u, v) if u < v else (v, u))

    # Variable edges: cannot select both a literal and its negation.
    positive = {}
    negative = {}
    for vertex, literal in enumerate(literal_of):
        if literal > 0:
            positive.setdefault(literal, []).append(vertex)
        else:
            negative.setdefault(-literal, []).append(vertex)
    for var, pos_verts in positive.items():
        for u in pos_verts:
            for v in negative.get(var, ()):
                edges.add((u, v) if u < v else (v, u))

    n = len(literal_of)
    return {"n": n, "edges": [list(e) for e in sorted(edges)], "k": len(clauses)}
