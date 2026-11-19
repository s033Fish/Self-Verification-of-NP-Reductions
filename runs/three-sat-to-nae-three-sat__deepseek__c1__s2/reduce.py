def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to NAE-3-SAT.

    For each source clause (l1, l2, l3), introduce a fresh variable y_i and
    add the two NAE-3 clauses:
        (l1, l2, y_i)
        (l3, t, -y_i)
    where t is a single new global variable.

    Together these two clauses enforce the 4-variable NAE constraint
    NAE(l1, l2, l3, t).  If t = 0, this says the original clause must be
    satisfied; if t = 1, it says the complemented clause must be satisfied.
    Because NAE-3-SAT is complement-symmetric, the constructed instance is
    satisfiable iff the original 3-SAT instance is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    # No clauses: the empty NAE formula is also a yes-instance.
    if k == 0:
        return {"num_vars": m, "clauses": []}

    t = m + 1
    new_clauses = []
    for i, (l1, l2, l3) in enumerate(clauses):
        y = m + 2 + i
        new_clauses.append([l1, l2, y])
        new_clauses.append([l3, t, -y])

    return {"num_vars": m + 1 + k, "clauses": new_clauses}
