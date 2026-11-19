"""Polynomial-time reduction from 3-Coloring to 3-SAT.

For a graph with n vertices introduce 3n colour variables

    x_{v,c} = 3*v + c + 1      (v in 0..n-1, c in 0..2)

meaning "vertex v receives colour c", plus one fresh padding variable
p = 3*n + 1, which is distinct from every colour variable.

Clauses:
  * (x_{v,0} v x_{v,1} v x_{v,2}) for every vertex v
        -- every vertex receives at least one colour.
  * (not x_{v,c} v not x_{v,d} v p) and
    (not x_{v,c} v not x_{v,d} v not p)
    for every vertex v and every pair of colours c < d
        -- together equivalent to (not x_{v,c} v not x_{v,d}),
           i.e. vertex v receives at most one colour.
  * (not x_{u,c} v not x_{v,c} v p) and
    (not x_{u,c} v not x_{v,c} v not p)
    for every edge {u,v} and every colour c
        -- together equivalent to (not x_{u,c} v not x_{v,c}),
           i.e. adjacent vertices do not share a colour.

The padding pair (core v p) ^ (core v not p) is equivalent to core for
any value of p, so reusing a single p is sound.  The construction uses
O(n + |E|) clauses and therefore runs in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 1
    p = num_vars  # fresh padding variable, distinct from all colour vars

    def var(v, c):
        return 3 * v + c + 1

    clauses = []

    for v in range(n):
        # At least one colour.
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # At most one colour: each 2-literal core is padded to 3 literals.
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-var(v, c), -var(v, d), p])
                clauses.append([-var(v, c), -var(v, d), -p])

    for u, v in edges:
        # Endpoints of an edge must receive different colours.
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c), p])
            clauses.append([-var(u, c), -var(v, c), -p])

    return {"num_vars": num_vars, "clauses": clauses}
