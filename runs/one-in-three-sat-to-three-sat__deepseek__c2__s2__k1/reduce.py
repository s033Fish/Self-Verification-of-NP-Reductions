def reduce(instance):
    """Polynomial-time reduction from positive 1-in-3-SAT to 3-SAT.

    For every source clause (a, b, c), the condition that exactly one of
    a, b, c is true is equivalent to the conjunction of these five clauses:

        ( a or  b or  c)   # at least one true
        (-a or -b or  c)   # not (a and b)
        (-a or  b or -c)   # not (a and c)
        ( a or -b or -c)   # not (b and c)
        (-a or -b or -c)   # not all three

    Each generated clause has exactly three literals on three different
    variables, so the result is a valid 3-SAT instance.
    """
    num_vars = instance["num_vars"]
    target_clauses = []

    for a, b, c in instance["clauses"]:
        target_clauses.append([a, b, c])
        target_clauses.append([-a, -b, c])
        target_clauses.append([-a, b, -c])
        target_clauses.append([a, -b, -c])
        target_clauses.append([-a, -b, -c])

    return {"num_vars": num_vars, "clauses": target_clauses}
