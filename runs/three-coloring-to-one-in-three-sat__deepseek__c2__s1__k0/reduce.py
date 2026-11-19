"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Source instance:
    {"n": n, "edges": [[u, v], ...]}

Target instance:
    {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v in 0..n-1 and colour c in {0, 1, 2}, introduce a Boolean
variable x[v, c], meaning "vertex v receives colour c".  These are numbered
1 .. 3n.

For every vertex v add the positive 1-in-3 clause

    (x[v,0], x[v,1], x[v,2]),

which forces exactly one colour to be chosen for v.

For every edge {u,v} and every colour c introduce one auxiliary variable
y[{u,v},c] and add the clause

    (x[u,c], x[v,c], y[{u,v},c]).

A 1-in-3 clause is satisfied exactly when one of its three variables is true.
Thus this clause forbids x[u,c] and x[v,c] from both being true; if exactly
one or neither of them is true, a suitable value for y exists.  Hence the
edge clauses say precisely that adjacent vertices must not receive the same
colour.

The construction is a proper reduction: a valid 3-colouring gives a
satisfying assignment by setting y true exactly when neither endpoint has
colour c, and any satisfying assignment restricts to a proper 3-colouring.

The number of variables is 3n + 3|E| and the number of clauses is
n + 3|E|, so the reduction runs in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 3 * len(edges)
    clauses = []

    # Exactly one colour for each vertex.
    for v in range(n):
        base = 3 * v + 1
        clauses.append([base, base + 1, base + 2])

    # Adjacent vertices must not share a colour.
    next_aux = 3 * n + 1
    for u, v in edges:
        for c in range(3):
            x_u = 3 * u + c + 1
            x_v = 3 * v + c + 1
            clauses.append([x_u, x_v, next_aux])
            next_aux += 1

    return {"num_vars": num_vars, "clauses": clauses}
