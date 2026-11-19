"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Source instance (OneInThreeSat):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
Target instance (ExactCover):
    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
For every variable i (1..m) and every occurrence t of i in the formula we
create two elements T(i,t) and F(i,t).  The element T(i,t) means "variable i
is true at its t-th occurrence", F(i,t) means "variable i is false there".

Variable gadget: for each variable i with k occurrences we add the element
G(i) and the two sets

    {G(i)} U {T(i,1), ..., T(i,k)}
    {G(i)} U {F(i,1), ..., F(i,k)}

Since G(i) occurs only in these two sets, exactly one of them is chosen.
This forces all occurrences of i to be covered on the same side: either the
gadget covers every T(i,·) (variable false everywhere) or every F(i,·)
(variable true everywhere).  Mixed coverage is impossible because the ports
already covered by clause sets would be covered twice.

Clause gadget: for each clause j = (a, b, c) we add the element C(j) and the
three sets

    {C(j), T(a,ta), F(b,tb), F(c,tc)}
    {C(j), F(a,ta), T(b,tb), F(c,tc)}
    {C(j), F(a,ta), F(b,tb), T(c,tc)}

where ta/tb/tc are the occurrence indices of a/b/c in clause j.  C(j) occurs
only in these three sets, so exactly one is chosen: exactly one of the three
variables is marked true and the other two false.  Combined with the variable
gadgets this yields an exact cover iff the formula has a satisfying assignment
with exactly one true variable per clause.

The instance has universe size 7*|clauses| + num_vars and
3*|clauses| + 2*num_vars sets, so the reduction is polynomial.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # counts[i] = number of occurrences of variable i seen so far.
    counts = [0] * (num_vars + 1)
    # occ[j][p] = occurrence index (1-based) of the p-th variable of clause j.
    occ = []
    for clause in clauses:
        row = []
        for v in clause:
            counts[v] += 1
            row.append(counts[v])
        occ.append(row)

    next_id = 0

    # Element for the variable gadget of each variable.
    gadget = {}
    for i in range(1, num_vars + 1):
        gadget[i] = next_id
        next_id += 1

    # Occurrence ports.
    true_port = {}
    false_port = {}
    for i in range(1, num_vars + 1):
        for t in range(1, counts[i] + 1):
            true_port[(i, t)] = next_id
            next_id += 1
            false_port[(i, t)] = next_id
            next_id += 1

    # Element for each clause.
    clause_elem = []
    for _ in clauses:
        clause_elem.append(next_id)
        next_id += 1

    sets = []

    # Variable gadgets.
    for i in range(1, num_vars + 1):
        k = counts[i]
        sets.append([gadget[i]] + [true_port[(i, t)] for t in range(1, k + 1)])
        sets.append([gadget[i]] + [false_port[(i, t)] for t in range(1, k + 1)])

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        a, b, c = clause
        ta, tb, tc = occ[j]
        ce = clause_elem[j]
        sets.append([ce, true_port[(a, ta)], false_port[(b, tb)], false_port[(c, tc)]])
        sets.append([ce, false_port[(a, ta)], true_port[(b, tb)], false_port[(c, tc)]])
        sets.append([ce, false_port[(a, ta)], false_port[(b, tb)], true_port[(c, tc)]])

    return {"universe_size": next_id, "sets": sets}
