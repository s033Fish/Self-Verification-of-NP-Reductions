"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Construction
------------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a Boolean
variable x_{v,c}, meaning "vertex v gets colour c".  Number them so that
x_{v,c} = 3*v + c + 1.

Clauses:
  * For each vertex v:  (x_{v,0} or x_{v,1} or x_{v,2})
    -- every vertex must receive at least one colour.
  * For each edge (u,v) and each colour c:
        (not x_{u,c} or not x_{v,c})
    -- the two endpoints may not both receive colour c.

The edge clauses are only 2 literals long, so each is padded to a proper
3-literal clause using one shared fresh variable z = 3*n + 1:

        (a or b)  ==  (a or b or z) and (a or b or not z)

for the two literals a = not x_{u,c}, b = not x_{v,c}.  The two padded
clauses are satisfiable exactly when a or b is true, no matter how z is
assigned (if a or b were false, z would have to be both true and false),
so sharing z across all edge clauses is sound.

Correctness
-----------
(=>) A satisfying assignment makes at least one x_{v,c} true per vertex.
Pick colour(v) = some true colour of v.  For any edge (u,v), if both
endpoints had the same chosen colour c, then x_{u,c} and x_{v,c} would
both be true, contradicting the padded edge clause for colour c.  Hence
the chosen colours form a proper 3-colouring.

(<=) Given a proper 3-colouring, set x_{v,colour(v)} = true and all other
x variables false, and set z = false.  Every vertex clause holds; for an
edge (u,v) and colour c, at most one of x_{u,c}, x_{v,c} is true because
colour(u) != colour(v), so at least one of the two negative literals in
the edge clause is true.  All clauses are satisfied.

The construction uses 3*n + 1 variables and n + 6*|E| clauses, so it runs
in polynomial time and never calls a solver.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 1
    z = num_vars  # shared padding variable

    clauses = []

    # At least one colour for every vertex.
    for v in range(n):
        base = 3 * v
        clauses.append([base + 1, base + 2, base + 3])

    # Adjacent vertices must not share a colour.  Each 2-literal clause is
    # padded to two 3-literal clauses with the shared variable z.
    for u, v in edges:
        for c in range(3):
            a = -(3 * u + c + 1)
            b = -(3 * v + c + 1)
            clauses.append([a, b, z])
            clauses.append([a, b, -z])

    return {"num_vars": num_vars, "clauses": clauses}
