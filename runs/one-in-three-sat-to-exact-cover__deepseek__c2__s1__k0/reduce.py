"""Polynomial-time reduction from positive 1-in-3-SAT to Exact Cover.

Construction
------------
Let the source instance have ``m`` variables and ``k`` clauses.

Universe (size ``m + k``):
  * element ``i - 1`` for each variable ``i`` in ``1..m``;
  * element ``m + j`` for each clause ``j`` in ``0..k-1``.

Sets:
  * for each variable ``i``, a "true" set
        {i - 1} U {m + j : variable i occurs in clause j};
  * for each variable ``i``, a "false" set
        {i - 1}.

Correctness
-----------
The true and false sets of a variable share its variable element, so an
exact cover must choose exactly one of them; this is the truth value of
the variable.  A clause element ``m + j`` is contained in the true set of
exactly the variables occurring in clause ``j``.  Therefore it is covered
exactly once iff exactly one of those variables is assigned true.  Hence
the exact cover instance is a yes-instance iff the 1-in-3-SAT instance is.
"""


def reduce(instance):
    """Return an Exact Cover instance equivalent to the given 1-in-3-SAT one."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    universe_size = num_vars + num_clauses
    sets = []

    for var in range(1, num_vars + 1):
        var_element = var - 1

        true_set = [var_element]
        for clause_index, clause in enumerate(clauses):
            if var in clause:
                true_set.append(num_vars + clause_index)

        false_set = [var_element]

        sets.append(true_set)
        sets.append(false_set)

    return {"universe_size": universe_size, "sets": sets}
