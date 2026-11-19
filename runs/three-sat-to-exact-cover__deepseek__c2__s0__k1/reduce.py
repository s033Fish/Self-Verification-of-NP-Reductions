"""Polynomial-time reduction from 3-SAT to Exact Cover."""


def reduce(instance):
    """Reduce a 3-SAT instance to an Exact Cover instance.

    Element ids:
      variable i (1-based)  -> i - 1
      occurrence (j, k)     -> m + 3*j + k
      clause j              -> m + 3*n + j

    For each variable there are two assignment sets.  The true set covers
    all occurrences of the negative literal, and the false set covers all
    occurrences of the positive literal.  Thus a literal occurrence is
    available to a clause set exactly when that literal is true.

    For each literal occurrence there is a clause set {clause, occurrence}
    and a singleton {occurrence}.  The singleton lets unused true
    occurrences be covered without interfering with clause sets.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    universe_size = m + 4 * n

    # true_sets[i] is chosen when variable i+1 is true.
    # false_sets[i] is chosen when variable i+1 is false.
    true_sets = [[i] for i in range(m)]
    false_sets = [[i] for i in range(m)]

    sets = []
    for j, clause in enumerate(clauses):
        for k, lit in enumerate(clause):
            occ = m + 3 * j + k
            clause_elem = m + 3 * n + j

            if lit > 0:
                # Positive literal is false when the variable is false.
                false_sets[lit - 1].append(occ)
            else:
                # Negative literal is false when the variable is true.
                true_sets[-lit - 1].append(occ)

            # Cover the clause element together with this occurrence.
            sets.append([clause_elem, occ])
            # Cover this occurrence if no clause set uses it.
            sets.append([occ])

    for i in range(m):
        sets.append(true_sets[i])
        sets.append(false_sets[i])

    return {"universe_size": universe_size, "sets": sets}
