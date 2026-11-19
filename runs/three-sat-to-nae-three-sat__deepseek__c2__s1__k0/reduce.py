def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to NAE-3-SAT.

    For each clause (l1, l2, l3) of the source instance, introduce a fresh
    variable y_i and add the two NAE clauses:
        (l1, l2, y_i)
        (-y_i, l3, f)
    where f is a single global fresh variable.

    If f is false, these two clauses are satisfiable exactly when
    (l1 or l2 or l3) is true.  If f is true, they enforce the complement
    clause (not l1 or not l2 or not l3), which does not change
    satisfiability because a 3-SAT formula is satisfiable iff its
    complement is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    f_var = m + 1
    new_clauses = []

    for i, clause in enumerate(clauses):
        y_var = m + 2 + i
        l1, l2, l3 = clause
        new_clauses.append([l1, l2, y_var])
        new_clauses.append([-y_var, l3, f_var])

    return {"num_vars": m + 1 + k, "clauses": new_clauses}
