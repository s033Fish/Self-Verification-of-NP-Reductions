"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover."""


def reduce(instance):
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    For every variable we create a selector element and force exactly one
    of two variable sets to be chosen.  For every occurrence of a variable
    in a clause we create a true-copy element and a false-copy element.
    Choosing the variable's true set covers all true copies; choosing its
    false set covers all false copies.

    For a clause (a, b, c), the three possible clause sets are
        {a_false, b_true,  c_true}
        {a_true,  b_false, c_true}
        {a_true,  b_true,  c_false}
    Each set corresponds to exactly one of the three variables being true.
    The clause sets pairwise overlap, so at most one can be chosen.  The
    uncovered copies of a clause can be covered by one of these sets
    exactly when exactly one of the clause's variables is true.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # occurrences[var] is a list of (true_key, false_key) pairs, one pair
    # for each occurrence of var in the formula.
    occurrences = {}
    clause_occurrences = []

    for clause_index, clause in enumerate(clauses):
        triple = []
        for position, var in enumerate(clause):
            true_key = ("t", clause_index, position)
            false_key = ("f", clause_index, position)
            occurrences.setdefault(var, []).append((true_key, false_key))
            triple.append((true_key, false_key))
        clause_occurrences.append(triple)

    element_index = {}
    elements = []

    def idx(key):
        if key not in element_index:
            element_index[key] = len(elements)
            elements.append(key)
        return element_index[key]

    sets = []

    # Variable gadgets: exactly one of the two sets per variable can be
    # chosen because they share the selector element.
    for var in range(1, num_vars + 1):
        selector = idx(("s", var))
        true_keys = [t for t, _ in occurrences.get(var, [])]
        false_keys = [f for _, f in occurrences.get(var, [])]
        sets.append([selector] + [idx(k) for k in true_keys])
        sets.append([selector] + [idx(k) for k in false_keys])

    # Clause gadgets: each set makes exactly one of the three variables
    # true and covers the two false copies plus the true variable's false
    # copy.
    for triple in clause_occurrences:
        (t0, f0), (t1, f1), (t2, f2) = triple
        sets.append([idx(f0), idx(t1), idx(t2)])
        sets.append([idx(t0), idx(f1), idx(t2)])
        sets.append([idx(t0), idx(t1), idx(f2)])

    return {"universe_size": len(elements), "sets": sets}
