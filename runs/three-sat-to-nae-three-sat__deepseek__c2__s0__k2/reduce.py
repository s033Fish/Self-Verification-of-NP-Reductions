"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Construction
------------
Let the source instance have ``m`` variables and clauses ``C_1, ..., C_k``.
Introduce one global variable ``g = m + 1`` and, for each clause
``C_i = (l1, l2, l3)``, one fresh variable ``y_i = m + 1 + i``.

Replace ``C_i`` by the two NAE-3 clauses::

    NAE(l1, l2, y_i)
    NAE(-y_i, l3, g)

Correctness
-----------
The pair above is equivalent (over the choice of ``y_i``) to the NAE-4
clause ``NAE(l1, l2, l3, g)``: a 4-literal NAE clause
``NAE(a, b, c, d)`` holds iff there is a ``y`` with ``NAE(a, b, y)`` and
``NAE(-y, c, d)``.

With ``g = 0``, ``NAE(l1, l2, l3, 0)`` holds exactly when ``l1, l2, l3``
are not all false, i.e. exactly when ``(l1 or l2 or l3)`` holds.  NAE
clauses are invariant under complementing every variable, so whenever the
constructed formula is satisfiable there is also a satisfying assignment
with ``g = 0``.  Hence the NAE-3-SAT instance is satisfiable iff the
original 3-SAT instance is.

The construction uses ``m + 1 + k`` variables and ``2k`` clauses, so it
runs in linear (hence polynomial) time and never invokes a solver.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an equisatisfiable NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    global_var = num_vars + 1
    result_clauses = []
    for index, (l1, l2, l3) in enumerate(clauses):
        fresh = num_vars + 2 + index
        result_clauses.append([l1, l2, fresh])
        result_clauses.append([-fresh, l3, global_var])

    return {
        "num_vars": num_vars + 1 + len(clauses),
        "clauses": result_clauses,
    }
