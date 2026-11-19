"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (standard):
  * For every clause and every literal occurrence in it, create one vertex.
    (Occurrences are kept separate, so repeated literals and repeated clauses
    yield separate vertices.)
  * Add an edge between every pair of vertices that come from the SAME clause
    (a satisfying assignment may pick at most one true literal per clause).
  * Add an edge between every pair of vertices whose literals are
    complementary, i.e. v and -v (they cannot both be true).
  * Set k = number of clauses.

Correctness:
  (=>) Given a satisfying assignment, pick one true literal per clause. This
       selects exactly one vertex per clause, so no same-clause edge is used,
       and no two selected literals are complementary (both would be true),
       so the selected set is independent and has size = number of clauses.
  (<=) Given an independent set of size >= k = number of clauses, it can
       contain at most one vertex per clause, hence exactly one per clause
       (there are k clauses). Assign each variable the truth value that makes
       the chosen literal true; complementary edges guarantee consistency.
       Every clause then has a true literal, so the formula is satisfiable.

Edge cases:
  * No clauses: k = 0, graph has no vertices; k <= 0 -> yes (correct).
  * An empty clause contributes no vertices, so at most k-1 vertices can be
    chosen and the instance is no (correct).
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertex -> literal it represents
    literals = []
    # clause index -> list of vertices for that clause
    clause_vertices = []

    for clause in clauses:
        verts = []
        for lit in clause:
            v = len(literals)
            literals.append(lit)
            verts.append(v)
        clause_vertices.append(verts)

    n = len(literals)

    # Collect edges as unordered pairs, deduplicated.
    edge_set = set()

    def add_edge(a, b):
        if a == b:
            return
        edge_set.add((a, b) if a < b else (b, a))

    # Edges between vertices of the same clause.
    for verts in clause_vertices:
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                add_edge(verts[i], verts[j])

    # Edges between complementary literals.
    by_literal = {}
    for v, lit in enumerate(literals):
        by_literal.setdefault(lit, []).append(v)
    for lit, verts in by_literal.items():
        for other in by_literal.get(-lit, ()):
            for a in verts:
                add_edge(a, other)

    edges = [[a, b] for (a, b) in edge_set]

    return {"n": n, "edges": edges, "k": len(clauses)}
