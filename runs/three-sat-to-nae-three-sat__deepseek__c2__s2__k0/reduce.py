def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to NAE-3-SAT.

    Given a 3-SAT instance with m variables and clauses C_i = (a_i v b_i v c_i),
    introduce a global variable x and a fresh variable y_i for each clause.
    Replace each clause with two NAE-3-SAT clauses:
        NAE(a_i, b_i, y_i)
        NAE(-y_i, c_i, x)

    If x is false, the gadget is equivalent to a_i v b_i v c_i.
    If x is true, the gadget is equivalent to -a_i v -b_i v -c_i.
    The latter formula is satisfiable only if the original is satisfiable
    (complement the satisfying assignment), so the reduction is exact.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    new_clauses = []
    x = m + 1
    for i, (a, b, c) in enumerate(clauses):
        y = m + 2 + i
        new_clauses.append([a, b, y])
        new_clauses.append([-y, c, x])
    return {"num_vars": m + 1 + len(clauses), "clauses": new_clauses}
