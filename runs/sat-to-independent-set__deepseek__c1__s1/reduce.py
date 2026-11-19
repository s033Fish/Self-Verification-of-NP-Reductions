"""Polynomial-time reduction from SAT to Independent Set.

Construction (the standard one):
  * For every occurrence of a literal in a clause, create one vertex.
    Vertex ids are assigned in order of clause, then literal position.
  * Inside each clause, add an edge between every pair of its vertices,
    so an independent set can pick at most one literal per clause.
  * Between clauses, add an edge between every pair of contradictory
    literals (v and -v), so a consistent assignment is forced.
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause: these choices
are pairwise non-adjacent (one per clause, no contradictions), giving an
independent set of size = #clauses. Conversely, any independent set of
size k = #clauses must contain exactly one vertex per clause, and since
no contradictory pair is chosen, setting those literals true (and the
other variables arbitrarily) satisfies every clause.

Edge cases:
  * No clauses -> k = 0, empty graph -> yes (k <= 0).
  * Empty clause -> it contributes no vertex, so the maximum independent
    set is at most (#nonempty clauses) < k -> no.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 0
    # vertices[i] = list of vertex ids for clause i
    vertices = []
    for clause in clauses:
        ids = []
        for _literal in clause:
            ids.append(n)
            n += 1
        vertices.append(ids)

    edges = set()

    def add_edge(u, v):
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        edges.add((a, b))

    # Edges among literals of the same clause.
    for ids in vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                add_edge(ids[i], ids[j])

    # Edges between contradictory literals in different clauses.
    # Map literal value -> list of vertex ids carrying that literal.
    occurrences = {}
    for clause, ids in zip(clauses, vertices):
        for literal, vid in zip(clause, ids):
            occurrences.setdefault(literal, []).append(vid)

    for literal, vids in occurrences.items():
        opposite = occurrences.get(-literal)
        if not opposite:
            continue
        for u in vids:
            for v in opposite:
                add_edge(u, v)

    edge_list = [[u, v] for (u, v) in sorted(edges)]

    return {"n": n, "edges": edge_list, "k": len(clauses)}
