"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance (ThreeColoring):
    {"n": n, "edges": [[u, v], ...]}
    Vertices 0..n-1, undirected edges between distinct vertices.

Target instance (ThreeSat):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Variables 1..m, every clause exactly 3 literals on 3 distinct
    variables.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0, 1, 2} introduce the
variable

    x_{v,c} = 3*v + c + 1

meaning "vertex v is given colour c".

* At least one colour per vertex: for every v add the clause
      (x_{v,0} OR x_{v,1} OR x_{v,2}).

* Adjacent vertices must not share a colour: for every edge {u, v} and
  every colour c add the binary constraint
      (NOT x_{u,c} OR NOT x_{v,c}).

The target format demands exactly three literals on three different
variables, so each binary constraint C = (NOT x_{u,c} OR NOT x_{v,c}) is
replaced by the two clauses

      (C OR y),  (C OR NOT y)

using a single fresh variable y shared by all such constraints.  For any
assignment of the x variables the pair is satisfiable (over y) exactly
when C is: if C is true both clauses hold for either value of y, while if
C is false the two clauses force y and NOT y simultaneously.  Hence the
replacement preserves satisfiability.

Correctness
-----------
If the graph has a proper 3-colouring, set x_{v,c} true iff v has colour
c.  Every vertex clause holds, and for each edge the endpoints have
different colours so no colour is shared; the padded clauses are then
satisfiable.  Conversely, if the formula is satisfiable, every vertex has
at least one true colour, and for every edge {u, v} and colour c the
constraint forbids x_{u,c} and x_{v,c} from both being true.  Picking one
true colour per vertex therefore gives a proper 3-colouring.

The construction uses O(n + |E|) variables and clauses and runs in
O(n + |E|) time, so it is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    # Every vertex gets at least one of the three colours.
    for v in range(n):
        base = 3 * v + 1
        clauses.append([base, base + 1, base + 2])

    # Every edge forbids its endpoints from sharing a colour.  Each
    # binary clause is padded to three literals with one shared fresh
    # variable, using the equivalence C == (C OR y) AND (C OR NOT y).
    if edges:
        y = num_vars + 1
        num_vars += 1
        for u, v in edges:
            for c in range(3):
                a = -(3 * u + c + 1)
                b = -(3 * v + c + 1)
                clauses.append([a, b, y])
                clauses.append([a, b, -y])

    return {"num_vars": num_vars, "clauses": clauses}
