"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (standard):
  * For every occurrence of a literal in a clause, create one vertex.
  * Within a clause, connect every pair of its vertices (a clique), so an
    independent set can select at most one vertex per clause.
  * Between any two vertices whose literals are complementary (v and -v),
    add an edge, so an independent set cannot select contradictory literals.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size k by choosing one
true literal occurrence per clause (no two chosen literals are contradictory).
Conversely, an independent set of size k selects exactly one vertex per clause
and contains no contradictory pair, so setting all selected literals to true
gives a satisfying assignment.

Edge cases:
  * No clauses -> k = 0, which is always a yes for Independent Set.
  * An empty clause contributes no vertex, so at most (#nonempty clauses) < k
    vertices can be selected, correctly giving a no.
"""


def reduce(instance):
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # Create one vertex per literal occurrence, remembering its literal.
    vertex_literal = []
    clause_vertices = []
    for clause in clauses:
        ids = []
        for literal in clause:
            ids.append(len(vertex_literal))
            vertex_literal.append(literal)
        clause_vertices.append(ids)

    n = len(vertex_literal)
    edges = set()

    def add_edge(u, v):
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.add((u, v))

    # Clique edges inside each clause.
    for ids in clause_vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                add_edge(ids[i], ids[j])

    # Conflict edges between complementary literals.
    literal_vertices = {}
    for vertex, literal in enumerate(vertex_literal):
        literal_vertices.setdefault(literal, []).append(vertex)

    for literal, vertices in literal_vertices.items():
        opposite = literal_vertices.get(-literal)
        if opposite is None:
            continue
        for u in vertices:
            for v in opposite:
                add_edge(u, v)

    k = len(clauses)
    return {
        "n": n,
        "edges": [[u, v] for u, v in sorted(edges)],
        "k": k,
    }
