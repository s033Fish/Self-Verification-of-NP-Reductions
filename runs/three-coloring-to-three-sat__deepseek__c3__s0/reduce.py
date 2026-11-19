"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For every vertex v and colour c in {0,1,2} introduce a boolean variable
x[v,c] meaning "vertex v gets colour c".

  * At least one colour per vertex:      (x[v,0] v x[v,1] v x[v,2])
  * At most one colour per vertex:       (~x[v,c] v ~x[v,d] v D)   for c < d
  * Proper edge colouring:               (~x[u,c] v ~x[v,c] v D)   for each edge {u,v}

The literal D is a fresh variable that is forced to be false by four
auxiliary clauses over D and two more fresh variables P, Q.  Because D is
always false, every padded 2-clause above is equivalent to the original
2-clause, so the formula is satisfiable exactly when the graph is
3-colourable.  The construction uses O(n + |E|) variables and clauses.
"""


def reduce(instance):
    """Map a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def x(v, c):
        # 1-based variable index for "vertex v has colour c"
        return 3 * v + c + 1

    num_vars = 3 * n + 3
    D = 3 * n + 1  # forced-false padding variable
    P = 3 * n + 2  # auxiliary variable
    Q = 3 * n + 3  # auxiliary variable

    clauses = []

    # Force D = false: if D were true these four clauses would require both
    # Q and ~Q, which is impossible.
    clauses.append([-D, P, Q])
    clauses.append([-D, -P, Q])
    clauses.append([-D, P, -Q])
    clauses.append([-D, -P, -Q])

    for v in range(n):
        # At least one colour.
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])
        # At most one colour (padded with the false literal D).
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-x(v, c), -x(v, d), D])

    # Adjacent vertices must differ in every colour.
    for u, w in edges:
        for c in range(3):
            clauses.append([-x(u, c), -x(w, c), D])

    return {"num_vars": num_vars, "clauses": clauses}
