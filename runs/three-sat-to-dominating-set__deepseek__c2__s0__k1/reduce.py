"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
Let the formula have m variables and C clauses.

* For every variable v (1..m) create two vertices, one for the literal +v
  and one for the literal -v, joined by an edge.  These two vertices have no
  other neighbours, so a dominating set must contain at least one of them.

* For every clause create a triangle of three new vertices, one per literal
  of the clause.  Each of these three vertices is joined to the literal
  vertex of the literal it represents.

Set k = m.  The graph has n = 2m + 3C vertices.

Correctness
-----------
If the formula is satisfiable, pick for every variable the literal vertex that
is made true.  This is m vertices.  It dominates both vertices of every
variable gadget, and for every clause at least one of its triangle vertices is
adjacent to a chosen literal vertex, hence the whole triangle is dominated.

Conversely, a dominating set of size at most m must contain at least one
vertex of each of the m variable gadgets, so it has size exactly m and contains
no clause vertex.  Choosing the literal of the selected vertex in each gadget
gives a well defined assignment; every clause triangle must be dominated by
some chosen literal vertex, so every clause contains a true literal.  Hence the
formula is satisfiable.

The construction is clearly polynomial in the size of the formula.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Literal vertex for variable v (1-indexed): +v -> 2*(v-1), -v -> 2*(v-1)+1
    def lit_vertex(literal):
        v = abs(literal)
        return 2 * (v - 1) + (0 if literal > 0 else 1)

    edges = []
    # Variable gadgets: an edge between the two literal vertices.
    for v in range(1, num_vars + 1):
        a = 2 * (v - 1)
        edges.append([a, a + 1])

    n = 2 * num_vars
    # Clause gadgets: a triangle, each vertex joined to its literal vertex.
    for clause in clauses:
        base = n
        n += 3
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])
        for offset, literal in enumerate(clause):
            edges.append([base + offset, lit_vertex(literal)])

    return {"n": n, "edges": edges, "k": num_vars}
