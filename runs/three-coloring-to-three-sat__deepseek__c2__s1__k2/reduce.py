"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Given a graph instance {"n": n, "edges": [[u, v], ...]}, introduce boolean
variables x_{v,c} meaning "vertex v has colour c" for v in 0..n-1 and
c in 0..2.  The reduction uses the standard encoding:

  * for every vertex v, the clause (x_{v,0} or x_{v,1} or x_{v,2}) says
    that v receives at least one colour;
  * for every edge (u, v) and every colour c, the clause
    (~x_{u,c} or ~x_{v,c} or F) says that u and v cannot both receive
    colour c, where F is an auxiliary variable forced to be false.

The variable F is forced false by the four clauses
(~F or A or B), (~F or ~A or B), (~F or A or ~B), (~F or ~A or ~B),
which are unsatisfiable when F is true.  Every clause therefore has
exactly three literals on three different variables.

The formula is satisfiable iff the graph is 3-colourable.  If the graph
has a proper 3-colouring, set exactly the corresponding x variables true
and F false.  Conversely, if the formula is satisfiable, F is false, each
vertex has at least one true colour, and the edge clauses guarantee that
choosing any true colour for each vertex gives a proper 3-colouring.

The construction uses 3*n + 3 variables and O(n + |E|) clauses, so it
runs in polynomial time.  The special case n = 0 returns the empty
formula, which is satisfiable.
"""


def reduce(instance):
    """Return a 3-SAT instance equivalent to the given 3-Coloring instance."""
    n = instance["n"]
    edges = instance["edges"]

    # A graph with no vertices is always 3-colourable; the empty formula
    # (num_vars = 0, no clauses) is satisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Variables 1..3n encode x_{v,c} = 3*v + c + 1.
    # Variables 3n+1, 3n+2, 3n+3 are the auxiliary variables F, A, B.
    def x(v, c):
        return 3 * v + c + 1

    false_var = 3 * n + 1
    aux_a = 3 * n + 2
    aux_b = 3 * n + 3
    num_vars = 3 * n + 3

    clauses = []

    # Force false_var to be false.  If it were true, these four clauses
    # would require all four combinations of aux_a and aux_b.
    clauses.append([-false_var, aux_a, aux_b])
    clauses.append([-false_var, -aux_a, aux_b])
    clauses.append([-false_var, aux_a, -aux_b])
    clauses.append([-false_var, -aux_a, -aux_b])

    # Each vertex must get at least one colour.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    # Adjacent vertices must not share a colour.  The false literal F pads
    # the two-literal constraint to a three-literal clause.
    for u, v in edges:
        for c in range(3):
            clauses.append([-x(u, c), -x(v, c), false_var])

    return {"num_vars": num_vars, "clauses": clauses}
