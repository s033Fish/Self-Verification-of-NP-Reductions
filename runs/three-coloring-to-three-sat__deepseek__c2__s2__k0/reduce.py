"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Target instance (3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Construction
------------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2} introduce a
boolean variable x(v, c), meaning "vertex v receives colour c":

    x(v, c) = 3*v + c + 1        (variables are 1-indexed)

Clauses:

1. At least one colour per vertex (3 literals, 3 distinct variables):
       (x(v,0) OR x(v,1) OR x(v,2))

2. At most one colour per vertex, for every pair c < d (2 literals):
       (NOT x(v,c) OR NOT x(v,d))

3. Different colours on the two endpoints of every edge, for each colour c:
       (NOT x(u,c) OR NOT x(v,c))

Clauses 2 and 3 have only two literals, but the target requires exactly three
literals on three different variables.  A two-literal clause (a OR b) is
replaced by the pair

       (a OR b OR y)  and  (a OR b OR NOT y)

where y is a single fresh variable (y = 3*n + 1) used for all such paddings.
The pair is satisfied by every assignment satisfying (a OR b); if (a OR b)
is false then y would have to be both true and false, so the pair is
unsatisfiable.  Thus the padding preserves satisfiability exactly.

The construction uses O(n^2 + |edges|) variables and clauses, so it runs in
polynomial time.  No solver is called.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Fresh padding variable, guaranteed different from every colour variable.
    pad = 3 * n + 1
    num_vars = pad

    clauses = []

    def add_padded(a, b):
        """Add (a OR b) as two 3-literal clauses using the padding variable."""
        clauses.append([a, b, pad])
        clauses.append([a, b, -pad])

    for v in range(n):
        base = 3 * v + 1  # x(v,0), x(v,1), x(v,2) are base, base+1, base+2

        # 1. At least one colour.
        clauses.append([base, base + 1, base + 2])

        # 2. At most one colour.
        add_padded(-base, -(base + 1))
        add_padded(-base, -(base + 2))
        add_padded(-(base + 1), -(base + 2))

    # 3. Edge endpoints must differ in colour.
    for u, v in edges:
        bu = 3 * u + 1
        bv = 3 * v + 1
        for c in range(3):
            add_padded(-(bu + c), -(bv + c))

    return {"num_vars": num_vars, "clauses": clauses}
