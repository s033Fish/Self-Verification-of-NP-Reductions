"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard "clause gadget" reduction):

Given a 3-SAT instance with ``num_vars`` variables and clauses C_1..C_c,
build a graph with one vertex per literal occurrence, i.e. 3 vertices for
each clause.  Vertex ``3*i + j`` corresponds to the j-th literal of clause i.

Edges:
  * Within each clause, connect all three vertices in a triangle.  Any
    independent set therefore contains at most one vertex per clause.
  * Between clauses, connect two vertices whose literals are contradictory
    (v and -v).  This forbids choosing an assignment that makes both a
    literal and its negation true.

Set ``k = c`` (the number of clauses).

A satisfying assignment yields an independent set of size c by picking, in
every clause, one literal that is true.  Conversely, an independent set of
size c must pick exactly one vertex per clause (triangles), and the
contradiction edges guarantee the chosen literals are mutually consistent,
so they define a satisfying assignment.  Hence the graph has an independent
set of size at least c iff the formula is satisfiable.

Edge cases:
  * No clauses: k = 0, empty graph -> k <= 0 is yes, matching satisfiability.
  * k is never negative here, and k <= n always (n = 3c >= c), so the
    target's k <= 0 / k > n special cases never distort the answer.
"""


def reduce(instance):
    """Map a 3-SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    n = 3 * num_clauses
    edges = []

    # Map each vertex to its literal.
    literals = []
    for clause in clauses:
        for lit in clause:
            literals.append(lit)

    for i in range(n):
        for j in range(i + 1, n):
            same_clause = (i // 3) == (j // 3)
            contradictory = literals[i] == -literals[j]
            if same_clause or contradictory:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": num_clauses}
