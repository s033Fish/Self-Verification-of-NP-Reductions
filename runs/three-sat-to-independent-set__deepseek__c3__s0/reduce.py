"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause, create a triangle of 3 vertices, one per literal.
  * For every variable v, join every vertex labelled +v to every vertex
    labelled -v (consistency edges).
  * Set k = number of clauses.

A satisfying assignment picks exactly one true literal per clause; those
vertices are pairwise non-adjacent (one per triangle, and no two chosen
literals are complementary).  Conversely any independent set of size k
must contain exactly one vertex per triangle (triangles cap it at one),
and the consistency edges force a consistent assignment, which satisfies
every clause.  Hence the graph has an independent set of size >= k iff the
formula is satisfiable.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    edges = []
    # literal -> list of vertex ids carrying that literal
    literal_vertices = {}
    n = 0

    for clause in clauses:
        verts = []
        for literal in clause:
            verts.append(n)
            literal_vertices.setdefault(literal, []).append(n)
            n += 1
        # Triangle: at most one literal of a clause may be chosen.
        edges.append([verts[0], verts[1]])
        edges.append([verts[1], verts[2]])
        edges.append([verts[0], verts[2]])

    # Consistency edges between complementary literals.  Process each
    # unordered pair of literal classes once to avoid duplicate edges.
    for literal, verts in literal_vertices.items():
        complement = -literal
        if literal < complement and complement in literal_vertices:
            for u in verts:
                for v in literal_vertices[complement]:
                    edges.append([u, v])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}
