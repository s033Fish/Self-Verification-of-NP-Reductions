"""Polynomial-time reduction from 3-SAT to positive 1-in-3-SAT.

Construction
------------
For each source variable i (1..n) create two target variables:
    i        meaning "source variable i is true"
    n + i    meaning "source variable i is false"

A single global variable d is forced to be false by the gadget
    (d, a, b), (a, b, c), (a, b, c'), (c, c', e).
If d = 1 then a = b = 0, hence c = c' = 1 and (c, c', e) is violated;
if d = 0 the gadget is satisfiable, e.g. a=1, b=0, c=0, c'=0, e=1.

With d = 0 the clause (i, n+i, d) forces exactly one of i, n+i to be
true, so the two rails of each source variable are consistent.

For each source clause (l1, l2, l3) add fresh "selector" variables
l1', l2', l3' and fresh helpers x1, x2, x3 together with the clauses
    (lk', not(lk), xk)   for k = 1, 2, 3
    (l1', l2', l3')
where not(lk) is the target variable representing the negation of the
literal lk.  The first three clauses enforce lk' -> lk, so the last
clause (exactly one of the lk' is true) is satisfiable iff at least one
source literal is true.  Hence the target is satisfiable iff the source
is.
"""


def reduce(instance):
    n = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = 2 * n + 1

    d = next_var
    next_var += 1
    a = next_var
    next_var += 1
    b = next_var
    next_var += 1
    c = next_var
    next_var += 1
    cp = next_var
    next_var += 1
    e = next_var
    next_var += 1

    target = []

    # Force d = 0.
    target.append([d, a, b])
    target.append([a, b, c])
    target.append([a, b, cp])
    target.append([c, cp, e])

    # Exactly one of i, n+i (the two rails of source variable i).
    for i in range(1, n + 1):
        target.append([i, n + i, d])

    for clause in clauses:
        lps = []
        xs = []
        for _ in range(3):
            lp = next_var
            next_var += 1
            x = next_var
            next_var += 1
            lps.append(lp)
            xs.append(x)
        for k in range(3):
            lit = clause[k]
            if lit > 0:
                neg = n + lit      # negation of "+lit"
            else:
                neg = -lit         # negation of "-lit"
            target.append([lps[k], neg, xs[k]])
        target.append([lps[0], lps[1], lps[2]])

    return {"num_vars": next_var - 1, "clauses": target}
