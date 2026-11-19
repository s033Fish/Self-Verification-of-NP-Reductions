"""Polynomial-time reduction from 3-SAT to Exact Cover.

Source instance:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance:  {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Elements
  * m_v            : one "mode" element per variable v = 1..m
  * o[j][k]        : one occurrence element for literal k of clause j
  * c_j            : one clause element per clause j

Sets
  * For each variable v, two mode sets sharing m_v:
        S_v_true  = {m_v} U {o[j][k] : clause j literal k is -v}
        S_v_false = {m_v} U {o[j][k] : clause j literal k is +v}
    Both contain m_v, so exactly one is chosen.  Choosing S_v_true means v is
    true and covers every occurrence of the *false* literal -v, leaving all
    occurrences of +v available to clause sets (and vice versa).

  * For each clause j and each nonempty subset S of its three literals:
        {c_j} U {o[j][k] : k in S}

Correctness
  * Satisfiable -> exact cover: pick the mode set matching the assignment and,
    for each clause, the subset consisting of its true literals.  The chosen
    occurrence elements are exactly the true literals' occurrences, which the
    mode sets left uncovered, so everything is disjoint and the whole universe
    is covered.
  * Exact cover -> satisfiable: m_v forces exactly one mode set per variable,
    defining an assignment.  Each c_j must be covered by one of its clause
    sets, which contains at least one occurrence element; disjointness means
    that occurrence was not covered by a mode set, i.e. its literal is true.
    Hence every clause is satisfied.

The construction is linear/quadratic in the input size, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Assign element ids.
    mode = {}
    for v in range(1, num_vars + 1):
        mode[v] = len(mode)  # ids 0..num_vars-1

    next_id = num_vars

    clause_elem = []
    occ = []  # occ[j][k] = element id of the k-th literal of clause j
    for clause in clauses:
        clause_elem.append(next_id)
        next_id += 1
        row = []
        for _ in range(3):
            row.append(next_id)
            next_id += 1
        occ.append(row)

    universe_size = next_id
    sets = []

    # Variable mode sets.
    for v in range(1, num_vars + 1):
        positive = []  # occurrences of +v
        negative = []  # occurrences of -v
        for j, clause in enumerate(clauses):
            for k, literal in enumerate(clause):
                if literal == v:
                    positive.append(occ[j][k])
                elif literal == -v:
                    negative.append(occ[j][k])
        # v true: cover m_v and all -v occurrences, leave +v available.
        sets.append([mode[v]] + negative)
        # v false: cover m_v and all +v occurrences, leave -v available.
        sets.append([mode[v]] + positive)

    # Clause sets: clause element plus any nonempty subset of its occurrences.
    for j in range(len(clauses)):
        for mask in range(1, 8):
            subset = [clause_elem[j]]
            for k in range(3):
                if (mask >> k) & 1:
                    subset.append(occ[j][k])
            sets.append(subset)

    return {"universe_size": universe_size, "sets": sets}
