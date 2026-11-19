def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to Exact Cover.

    Source instance:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Target instance:
        {"universe_size": u, "sets": [[element, ...], ...]}

    Construction:
      * One element per variable: v_i.
      * One element per clause: c_j.
      * One element per literal occurrence in the formula: o_{j,k}.
      * For each variable x_i, two variable sets:
            {v_i} union {occurrences of x_i}
            {v_i} union {occurrences of -x_i}
        Choosing the first covers all positive occurrences, meaning x_i is false.
        Choosing the second covers all negative occurrences, meaning x_i is true.
      * For each literal occurrence o in clause c_j, one clause set {o, c_j}.
        To cover c_j exactly once, one literal occurrence of that clause must be
        chosen. It can be chosen only if that occurrence was not already covered
        by the variable gadget, i.e. only if the literal is true.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    total_occurrences = sum(len(clause) for clause in clauses)

    # Element layout:
    #   0 .. m-1                         : variable elements v_i
    #   m .. m+n-1                       : clause elements c_j
    #   m+n .. m+n+total_occurrences-1   : literal occurrence elements
    universe_size = m + n + total_occurrences

    pos_occurrences = [[] for _ in range(m)]
    neg_occurrences = [[] for _ in range(m)]
    clause_occurrences = []

    offset = 0
    for clause in clauses:
        occs = []
        for lit in clause:
            occ = m + n + offset
            offset += 1
            occs.append(occ)

            var = abs(lit) - 1
            if lit > 0:
                pos_occurrences[var].append(occ)
            else:
                neg_occurrences[var].append(occ)
        clause_occurrences.append(occs)

    sets = []

    # Variable gadgets.
    for i in range(m):
        sets.append([i] + pos_occurrences[i])
        sets.append([i] + neg_occurrences[i])

    # Clause gadgets.
    for j, occs in enumerate(clause_occurrences):
        clause_element = m + j
        for occ in occs:
            sets.append([occ, clause_element])

    return {"universe_size": universe_size, "sets": sets}
