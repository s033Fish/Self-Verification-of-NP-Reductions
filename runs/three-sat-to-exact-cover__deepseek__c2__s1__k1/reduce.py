def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to Exact Cover.

    Source instance format:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Target instance format:
        {"universe_size": u, "sets": [[element, ...], ...]}

    Construction
    ------------
    Let n = num_vars and let the clauses be C_0, ..., C_{m-1}.

    Universe (size u = n + 4*m):
      * e_x = x - 1                for x = 1..n   (one per variable)
      * occ(j, k) = n + 3*j + k    for clause j, literal position k in {0,1,2}
      * c_j = n + 3*m + j          for clause j

    Sets:
      * Variable gadget, for each variable x:
          T_x = {e_x} U { occ(j,k) : literal at (j,k) is -x }
          F_x = {e_x} U { occ(j,k) : literal at (j,k) is +x }
        The shared element e_x forces exactly one of T_x / F_x to be chosen.
        Choosing T_x means "x is true": it covers all occurrences of the
        literal -x, leaving occurrences of +x free for the clause gadget.
        Choosing F_x means "x is false": symmetric.

      * Clause gadget, for each clause C_j and each literal occurrence occ(j,k):
          { occ(j,k) }            (singleton "absorber")
          { occ(j,k), c_j }       ("satisfier")
        An occurrence element is free exactly when its literal is true, so
        these sets are selectable exactly for true literals.  The clause
        element c_j can only be covered by a satisfier set, hence by a true
        literal.  The singleton absorbers let a clause with several true
        literals cover all of their occurrence elements while still using a
        single satisfier set for c_j.

    Correctness
    -----------
    (=>) Given a satisfying assignment, choose T_x/F_x according to the
    assignment.  For every clause pick one true literal and choose its
    satisfier set; choose the singleton absorber for every other true
    literal in the clause.  These sets are pairwise disjoint and cover the
    whole universe.

    (<=) In any exact cover, e_x is covered by exactly one of T_x/F_x,
    defining an assignment.  Each c_j must be covered by some satisfier set
    {occ(j,k), c_j}; the corresponding occurrence is therefore not covered
    by a variable gadget, so its literal is true.  Hence every clause is
    satisfied.

    The instance has 2*n + 6*m sets and universe size n + 4*m, both
    polynomial in the input size.
    """
    n = instance["num_vars"]
    clauses = instance["clauses"]
    m = len(clauses)

    u = n + 4 * m

    pos_occ = {v: [] for v in range(1, n + 1)}
    neg_occ = {v: [] for v in range(1, n + 1)}

    clause_data = []  # list of (clause_element, [occurrence elements])
    for j, clause in enumerate(clauses):
        c_elem = n + 3 * m + j
        occs = []
        for k, lit in enumerate(clause):
            occ = n + 3 * j + k
            occs.append(occ)
            v = abs(lit)
            if lit > 0:
                pos_occ[v].append(occ)
            else:
                neg_occ[v].append(occ)
        clause_data.append((c_elem, occs))

    sets = []

    # Variable gadget.
    for v in range(1, n + 1):
        e = v - 1
        # T_v: v is true  -> cover e_v and all negative occurrences of v
        sets.append([e] + neg_occ[v])
        # F_v: v is false -> cover e_v and all positive occurrences of v
        sets.append([e] + pos_occ[v])

    # Clause gadget.
    for c_elem, occs in clause_data:
        for occ in occs:
            sets.append([occ])            # absorber
            sets.append([occ, c_elem])    # satisfier

    return {"universe_size": u, "sets": sets}
