"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source (NAE-3-SAT): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target (3-Coloring): {"n": n, "edges": [[u, v], ...]}

Construction
------------
We build a graph whose proper 3-colourings correspond exactly to the
not-all-equal assignments of the formula.

* A base triangle on vertices T=0, F=1, B=2 pins down three distinct
  colours (think "true", "false", "base").

* For every variable v in 1..m we create two literal vertices,
  pos(v) for the literal +v and neg(v) for the literal -v.  Both are
  joined to B and to each other.  Hence neither can take B's colour and
  they must receive the two remaining colours, i.e. one is coloured like
  T and the other like F.  This encodes a consistent truth value.

* For every clause (l1, l2, l3) we add three fresh vertices u1, u2, u3
  forming a triangle, and connect ui to the literal vertex of li.

  If all three literals shared one colour c (all true or all false), then
  each ui would have to avoid c and could use only the other two colours;
  three mutually adjacent vertices cannot be coloured with two colours.
  So the clause gadget forbids the all-equal case.  If the literals are
  not all equal, the triangle can always be coloured (one ui takes the
  colour opposite to the majority / the two colours available cover the
  triangle).  The gadgets use disjoint new vertices, so they are
  independent.

The graph has 3 + 2m + 3k vertices and 3 + 3m + 6k edges, so the
construction runs in polynomial time and never calls a solver.
"""


def reduce(instance):
    """Return a 3-Coloring instance that is yes iff the NAE-3-SAT instance is yes."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: colours "true", "false", "base".
    T, F, B = 0, 1, 2
    edges = [[T, F], [T, B], [F, B]]

    def pos(v):
        """Vertex representing literal +v (v in 1..num_vars)."""
        return 3 + 2 * (v - 1)

    def neg(v):
        """Vertex representing literal -v (v in 1..num_vars)."""
        return 3 + 2 * (v - 1) + 1

    # Variable gadgets: +v and -v are adjacent and both adjacent to B.
    for v in range(1, num_vars + 1):
        p, n = pos(v), neg(v)
        edges.append([p, n])
        edges.append([p, B])
        edges.append([n, B])

    # Clause gadgets.
    next_vertex = 3 + 2 * num_vars
    for clause in clauses:
        u1, u2, u3 = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        # Triangle among the three gadget vertices.
        edges.append([u1, u2])
        edges.append([u2, u3])
        edges.append([u1, u3])
        # Each gadget vertex is joined to its literal's vertex.
        for u, literal in zip((u1, u2, u3), clause):
            v = abs(literal)
            literal_vertex = pos(v) if literal > 0 else neg(v)
            edges.append([u, literal_vertex])

    return {"n": next_vertex, "edges": edges}
