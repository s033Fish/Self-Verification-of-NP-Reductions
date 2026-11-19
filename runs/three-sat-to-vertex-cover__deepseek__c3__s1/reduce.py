"""Polynomial-time reduction from 3-SAT (ThreeSat) to Vertex Cover.

Standard gadget reduction:

* For every variable v in 1..m create two vertices, one for the literal +v
  and one for -v, joined by an edge.  Any vertex cover must contain at least
  one of them, and a minimum cover contains exactly one.
* For every clause create a triangle on three fresh vertices, and connect each
  of those three vertices to the literal vertex of the corresponding literal.
  Covering the triangle needs at least two of its three vertices, and the one
  left out must have a true literal, otherwise the edge to its (false) literal
  vertex would be uncovered.
* Set k = m + 2 * (number of clauses).

A satisfying assignment yields a cover of size m + 2c: pick the vertex of the
FALSE literal for each variable (m vertices), and for each clause pick the two
triangle vertices other than the one whose literal is TRUE (2 per clause).

Conversely, a cover of size <= m + 2c must pick at least one vertex per
variable edge (m) and at least two per clause triangle (2c); equality forces
exactly one and exactly two.  The vertex left out of each clause triangle
names a literal that must be true (else the edge from it to the literal vertex
is uncovered).  Since exactly one of +v / -v is left out per variable, the
implied assignment is consistent and satisfies every clause.  Hence the
formula is satisfiable iff the graph has a vertex cover of size at most k.

Duplicate clauses are redundant for satisfiability, so they are removed before
building the gadgets; this also keeps the edge list free of duplicates.
"""


def _literal_vertex(literal):
    """Map a non-zero literal to its vertex index."""
    variable = abs(literal)
    if literal > 0:
        return 2 * (variable - 1)          # vertex for "+v" (v is true)
    return 2 * (variable - 1) + 1          # vertex for "-v" (v is false)


def reduce(instance):
    """Reduce a ThreeSat instance to a VertexCover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Duplicate clauses do not change satisfiability and would only create
    # duplicate edges, so keep each distinct clause once.
    distinct = []
    seen_clauses = set()
    for clause in clauses:
        key = frozenset(clause)
        if key not in seen_clauses:
            seen_clauses.add(key)
            distinct.append(clause)

    edges = []
    seen_edges = set()

    def add_edge(u, v):
        key = (u, v) if u < v else (v, u)
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append([u, v])

    # Variable gadgets: one edge per variable.
    for variable in range(1, num_vars + 1):
        add_edge(2 * (variable - 1), 2 * (variable - 1) + 1)

    # Clause gadgets: a fresh triangle plus one edge to each literal vertex.
    next_vertex = 2 * num_vars
    for clause in distinct:
        a, b, c = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        add_edge(a, b)
        add_edge(a, c)
        add_edge(b, c)
        for triangle_vertex, literal in zip((a, b, c), clause):
            add_edge(triangle_vertex, _literal_vertex(literal))

    n = 2 * num_vars + 3 * len(distinct)
    k = num_vars + 2 * len(distinct)
    return {"n": n, "edges": edges, "k": k}
