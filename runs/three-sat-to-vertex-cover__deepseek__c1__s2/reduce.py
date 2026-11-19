"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (the standard one):

  * For every variable v in 1..m create two vertices, one standing for the
    literal +v and one for -v, joined by an edge (the variable gadget).
    Vertex 2*(v-1) is +v and vertex 2*(v-1)+1 is -v.
  * For every clause create a triangle on three fresh vertices, one per
    literal of that clause.
  * Join each triangle vertex to the variable-gadget vertex that represents
    the same literal.
  * Set k = m + 2 * (number of clauses).

Correctness:

  If an assignment satisfies every clause, take the true-literal vertex of
  each variable gadget (m vertices, covering every gadget edge) and, for each
  clause triangle, the two vertices other than a triangle vertex whose literal
  is true (2 per clause).  This covers all triangle edges and all clause to
  literal edges, so it is a vertex cover of size m + 2c.

  Conversely, any vertex cover of size at most m + 2c must use at least one
  endpoint of each of the m disjoint gadget edges and at least two vertices of
  each of the c disjoint triangles, so it has size exactly m + 2c and uses
  exactly one endpoint per gadget edge and exactly two per triangle.  For each
  clause the one omitted triangle vertex has its clause-to-literal edge covered
  by the chosen gadget endpoint, so that literal is true.  Assigning each
  variable the literal whose gadget endpoint was chosen therefore satisfies
  every clause.

  A formula with no clauses gives m disjoint edges and k = m, which is a yes
  instance exactly when the empty formula is satisfiable (including m = 0,
  where the graph is empty and k = 0).  Duplicate clauses simply become
  distinct triangles, preserving the equivalence.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Vertex Cover instance (yes iff yes)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    def literal_vertex(literal):
        # +v -> 2*(v-1), -v -> 2*(v-1)+1
        base = 2 * (abs(literal) - 1)
        return base if literal > 0 else base + 1

    edges = []

    # Variable gadgets: one edge per variable, joining +v and -v.
    for v in range(1, num_vars + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    # Clause gadgets: a triangle per clause, wired to the literal vertices.
    next_vertex = 2 * num_vars
    for clause in clauses:
        a, b, c = next_vertex, next_vertex + 1, next_vertex + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for offset, literal in enumerate(clause):
            edges.append([next_vertex + offset, literal_vertex(literal)])
        next_vertex += 3

    return {
        "n": next_vertex,
        "edges": edges,
        "k": num_vars + 2 * len(clauses),
    }
