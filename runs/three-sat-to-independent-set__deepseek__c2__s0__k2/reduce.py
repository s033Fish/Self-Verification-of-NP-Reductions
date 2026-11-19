"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause create three vertices, one per literal, and connect
    them in a triangle.  An independent set can therefore contain at most
    one vertex per clause.
  * For every pair of vertices whose literals are complementary (v and -v),
    add an edge.  This prevents choosing both a literal and its negation.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by
picking one true literal per clause.  Conversely an independent set of size
(#clauses) must pick exactly one vertex per clause triangle, and the
contradiction edges guarantee the chosen literals are simultaneously
satisfiable.  Hence the answer is preserved.

Edge cases:
  * No clauses -> n = 0, edges = [], k = 0, and k <= 0 is yes.
  * Duplicate clauses simply produce duplicate triangles, which is fine.
  * Variables not occurring in any clause are unconstrained and need no
    vertices.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance."""
    num_vars = instance["num_vars"]  # noqa: F841 (kept for clarity)
    clauses = instance["clauses"]

    edges = set()  # unordered pairs stored as (min, max) to avoid duplicates
    n = 0

    # Vertices for each clause: clause_vertices[i] = list of vertex ids
    clause_vertices = []
    for clause in clauses:
        verts = []
        for _literal in clause:
            verts.append(n)
            n += 1
        clause_vertices.append(verts)
        # Triangle on the three literal-vertices of this clause.
        a, b, c = verts
        edges.add((a, b))
        edges.add((a, c))
        edges.add((b, c))

    # Map each literal to the vertices representing it.
    literal_vertices = {}
    for clause, verts in zip(clauses, clause_vertices):
        for literal, vertex in zip(clause, verts):
            literal_vertices.setdefault(literal, []).append(vertex)

    # Contradiction edges between v and -v.  Iterate only over literals that
    # are positive (or, more generally, avoid processing both directions) by
    # relying on the set to deduplicate.
    for literal, verts in literal_vertices.items():
        opposite_verts = literal_vertices.get(-literal)
        if not opposite_verts:
            continue
        for u in verts:
            for w in opposite_verts:
                if u == w:
                    continue
                edges.add((u, w) if u < w else (w, u))

    edge_list = [[u, v] for (u, v) in sorted(edges)]
    return {"n": n, "edges": edge_list, "k": len(clauses)}
