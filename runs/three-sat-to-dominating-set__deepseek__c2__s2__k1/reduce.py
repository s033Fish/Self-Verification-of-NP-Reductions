"""Polynomial-time reduction from 3-SAT to Dominating Set.

Source instance (3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance (Dominating Set):
    {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
Let C be the number of clauses.

* For every variable v in 1..m create a triangle on three fresh vertices
  ``x_v`` (meaning "v is true"), ``n_v`` (meaning "v is false") and ``a_v``
  (an auxiliary vertex).  Vertex ids: 3*(v-1), 3*(v-1)+1, 3*(v-1)+2.

* For every clause j (0-based) create a triangle on three fresh vertices
  ``c_{j,0}``, ``c_{j,1}``, ``c_{j,2}``.  Vertex ids start at 3*m + 3*j.
  Connect ``c_{j,r}`` to the literal vertex of the r-th literal of clause j,
  where literal +v maps to ``x_v`` and literal -v maps to ``n_v``.

* Set k = m.

Correctness
-----------
(=>) Given a satisfying assignment, put in D, for each variable, the literal
vertex that is true.  |D| = m.  Every ``a_v`` is adjacent to a chosen literal
so each variable triangle is dominated.  Every clause has a true literal, so
the corresponding ``c_{j,r}`` is adjacent to a chosen vertex, and the other
two clause-gadget vertices are adjacent to it; hence every clause triangle is
dominated.  So D is a dominating set of size m.

(<=) In any dominating set D, the auxiliary vertex ``a_v`` can only be
dominated by ``x_v``, ``n_v`` or ``a_v`` itself.  These sets are disjoint over
variables, so |D| >= m.  If |D| <= m, then |D| = m and D contains exactly one
vertex of every variable triangle and no clause-gadget vertex.  Consider a
clause gadget {c0,c1,c2}; its vertices are adjacent only to each other and to
the clause's three literal vertices.  Since no c_r is in D, some literal of the
clause must be in D for the gadget to be dominated.  Map each variable to true
if its ``x_v`` is in D, false if its ``n_v`` is in D, and arbitrarily if
``a_v`` is in D.  Every clause contains a literal that is in D, and that literal
is made true by this assignment, so the formula is satisfiable.

The construction uses O(m + C) vertices and edges and runs in linear time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadgets: one triangle per variable.
    for v in range(1, num_vars + 1):
        base = 3 * (v - 1)
        x_v = base          # +v
        n_v = base + 1      # -v
        a_v = base + 2      # auxiliary
        edges.append([x_v, n_v])
        edges.append([x_v, a_v])
        edges.append([n_v, a_v])

    def literal_vertex(literal):
        v = abs(literal)
        base = 3 * (v - 1)
        return base if literal > 0 else base + 1

    # Clause gadgets: one triangle per clause, attached to its literals.
    for j, clause in enumerate(clauses):
        base = 3 * num_vars + 3 * j
        c0, c1, c2 = base, base + 1, base + 2
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c0, c2])
        for r, literal in enumerate(clause):
            edges.append([base + r, literal_vertex(literal)])

    n = 3 * num_vars + 3 * len(clauses)
    k = num_vars
    return {"n": n, "edges": edges, "k": k}
