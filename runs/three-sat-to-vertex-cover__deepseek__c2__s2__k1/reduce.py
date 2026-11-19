"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (clause triangles + consistency edges, via Independent Set):

Let the 3-SAT instance have ``c`` clauses.  For every literal occurrence we
create one graph vertex, so a 3-literal clause contributes three vertices.
The vertices of a clause form a triangle.

Edges:
  * the three edges of the triangle inside every clause, so an independent set
    can contain at most one vertex per clause;
  * for every variable ``v``, an edge between each occurrence of ``+v`` and
    each occurrence of ``-v``, so an independent set cannot pick contradictory
    literals.

Set ``k = (#vertices) - c`` (which is ``2c`` when every clause has three
literals).  A vertex cover of size at most ``k`` is exactly the complement of
an independent set of size at least ``c``.  Every independent set takes at
most one vertex per clause, hence at most ``c`` vertices, and one of size ``c``
exists iff the formula is satisfiable (choose one true literal per clause).
Hence the graph has a vertex cover of size at most ``k`` iff the formula is
satisfiable.
"""


def reduce(instance):
    clauses = instance["clauses"]

    edges = set()
    positive = {}  # variable -> list of vertices holding literal +v
    negative = {}  # variable -> list of vertices holding literal -v

    vertex = 0
    for clause in clauses:
        start = vertex
        for literal in clause:
            if literal > 0:
                positive.setdefault(literal, []).append(vertex)
            else:
                negative.setdefault(-literal, []).append(vertex)
            vertex += 1

        # Triangle over the clause's literal-occurrence vertices.
        vs = list(range(start, vertex))
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                edges.add(frozenset((vs[i], vs[j])))

    # Consistency edges: every +v occurrence conflicts with every -v occurrence.
    for var, pos_vertices in positive.items():
        for u in pos_vertices:
            for v in negative.get(var, ()):
                edges.add(frozenset((u, v)))

    n = vertex
    c = len(clauses)
    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - c,
    }
