def reduce(instance):
    """Polynomial-time reduction from 3-SAT to NAE-3-SAT.

    For each original clause (l1 or l2 or l3), introduce a fresh variable x.
    Also introduce one global variable y.  Emit the two NAE-3-SAT clauses:
        (l1, l2, x)
        (-x, l3, y)

    If the original formula is satisfiable, set y = false and choose each x
    appropriately.  Conversely, any satisfying assignment of the NAE formula
    can be complemented (which preserves NAE satisfaction) to one with y =
    false; under y = false the two clauses above force the original clause to
    be satisfied.  Hence the two instances have the same answer.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    y = m + 1
    new_clauses = []

    for i, clause in enumerate(clauses):
        l1, l2, l3 = clause
        x = m + 2 + i
        new_clauses.append([l1, l2, x])
        new_clauses.append([-x, l3, y])

    return {"num_vars": m + 1 + n, "clauses": new_clauses}
