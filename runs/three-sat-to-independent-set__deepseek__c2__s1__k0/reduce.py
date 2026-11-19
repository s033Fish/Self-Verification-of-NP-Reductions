"""Polynomial-time reduction from 3-SAT (SOURCE) to Independent Set (TARGET).

Construction (standard clause-triangle reduction):

  * For every clause c_i = (l1, l2, l3) create three vertices
    (3*i, 3*i+1, 3*i+2), one per literal occurrence.
  * Add the three edges of a triangle among those three vertices, so an
    independent set can pick at most one literal from each clause.
  * For every pair of vertices in *different* clauses whose literals are
    contradictory (x and -x), add an edge, so an independent set may not
    pick both.
  * Set k = number of clauses.

A set of k vertices with no internal edge must pick exactly one vertex from
each of the k clause triangles; the cross edges force the chosen literals to
be simultaneously satisfiable, and any satisfying assignment yields such a
set.  Hence the graph has an independent set of size >= k iff the formula is
satisfiable.

Edge cases:
  * No clauses: n = 0, edges = [], k = 0.  k <= 0 is always yes, matching
    the empty (satisfiable) formula.
  * Repeated clauses simply get their own triangles; the argument is
    unchanged because each triangle still contributes at most one vertex.

The construction uses O(#clauses) vertices and O(#clauses^2) edges, so it
runs in polynomial time and never calls a brute-force solver.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges = []
    seen = set()

    def add_edge(u, v):
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # Triangle for each clause: at most one literal per clause may be chosen.
    for i in range(len(clauses)):
        base = 3 * i
        add_edge(base, base + 1)
        add_edge(base + 1, base + 2)
        add_edge(base, base + 2)

    # Map each literal value to the vertices that represent it.
    literal_vertices = {}
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            literal_vertices.setdefault(literal, []).append(3 * i + j)

    # Edge between every pair of contradictory literals in different clauses.
    for literal, vertices in literal_vertices.items():
        for other in literal_vertices.get(-literal, ()):
            for u in vertices:
                for v in other:
                    add_edge(u, v)

    return {"n": n, "edges": edges, "k": len(clauses)}
