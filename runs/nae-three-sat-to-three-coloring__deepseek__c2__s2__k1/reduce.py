"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...]}

Construction
------------
Use three colours {0, 1, 2}.  Vertices 0, 1, 2 form a triangle, so they
receive all three colours; colour 2 is the "base" colour.

For every variable v we create two vertices pos[v] and neg[v].  They are
joined to each other and both are joined to the base vertex 2.  Hence
pos[v] and neg[v] must receive the two colours 0 and 1 (one each).  We
interpret colour 1 as "true".

For every clause (a, b, c) we create three fresh vertices p, q, r forming
a triangle, and connect p to a, q to b, r to c (where a literal +v maps to
pos[v] and -v maps to neg[-v]).  Because p, q, r form a triangle they must
get three distinct colours.  If a, b, c all had colour 0, then p, q, r
could only use colours {1, 2}; if they all had colour 1, only {0, 2}.  In
both cases three distinct colours are impossible.  If the literals are not
all equal, an explicit valid colouring of p, q, r exists.  Thus the gadget
is 3-colourable exactly when the clause is not all-equal.

Therefore the resulting graph is 3-colourable iff the NAE-3-SAT instance
is satisfiable.  The graph has 3 + 2m + 3k vertices and 3 + 3m + 6k edges
for m variables and k clauses, so the reduction runs in polynomial time.
"""


def reduce(instance):
    """Reduce an instance of NAE-3-SAT to an instance of 3-Coloring."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    def add(u, v):
        edges.append([u, v])

    # Base triangle: vertices 0, 1, 2 get the three distinct colours.
    # Vertex 2 acts as the base colour for the literal gadgets.
    add(0, 1)
    add(1, 2)
    add(2, 0)

    # Variable gadgets: pos[v] and neg[v] are forced to colours 0 and 1.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        p = 3 + 2 * (v - 1)
        q = p + 1
        pos[v] = p
        neg[v] = q
        add(p, q)   # one of them is colour 0, the other colour 1
        add(p, 2)   # neither may use the base colour 2
        add(q, 2)

    n = 3 + 2 * num_vars

    # Clause gadgets.
    for clause in clauses:
        a, b, c = (pos[lit] if lit > 0 else neg[-lit] for lit in clause)
        p, q, r = n, n + 1, n + 2
        n += 3
        add(p, q)   # triangle on the three fresh vertices
        add(q, r)
        add(r, p)
        add(p, a)   # attach the triangle to the clause's literals
        add(q, b)
        add(r, c)

    return {"n": n, "edges": edges}
