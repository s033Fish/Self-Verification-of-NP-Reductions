"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v and colour c in {0, 1, 2} introduce the variable

    x(v, c) = 3 * v + c + 1

The clause

    [x(v, 0), x(v, 1), x(v, 2)]

forces exactly one colour to be chosen for vertex v.

For every edge {u, v} and every colour c introduce a fresh auxiliary
variable p and the clause

    [x(u, c), x(v, c), p].

A 1-in-3 clause is true iff exactly one of its variables is true.  If
both x(u, c) and x(v, c) were true the clause would contain at least two
true variables and could not be satisfied, so the clause forbids the two
endpoints of an edge from sharing colour c.  If the two colour variables
are not both true, the fresh p can always be chosen to satisfy the clause
(p = 1 when both are false, p = 0 otherwise).  Each edge/colour pair has
its own p, so these auxiliary choices never interfere.

Therefore the produced formula is satisfiable iff the graph admits a
proper 3-colouring.  The construction uses O(n + |E|) variables and
clauses, so it runs in polynomial time.  No brute-force solver is used.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def vertex_var(v, c):
        # Vertex v, colour c -> a distinct positive variable in 1..3n.
        return 3 * v + c + 1

    clauses = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([vertex_var(v, 0), vertex_var(v, 1), vertex_var(v, 2)])

    # Fresh auxiliary variables start right after the 3n colour variables.
    num_vars = 3 * n

    # Adjacent vertices must not receive the same colour.
    for u, v in edges:
        for c in range(3):
            num_vars += 1
            clauses.append([vertex_var(u, c), vertex_var(v, c), num_vars])

    return {"num_vars": num_vars, "clauses": clauses}
