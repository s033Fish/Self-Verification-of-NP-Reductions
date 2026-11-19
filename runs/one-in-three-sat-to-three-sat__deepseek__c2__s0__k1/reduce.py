"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

A 1-in-3-SAT clause ``[a, b, c]`` demands that exactly one of ``a, b, c`` is
true.  This is the conjunction of:

  * at least one is true:  ``(a or b or c)``
  * no two are true:       ``(not a or not b)`` for every pair

The pairwise (2-literal) constraints are turned into proper 3-literal 3-SAT
clauses by padding them with one global fresh variable ``p``.  For a pair
``(x, y)`` we emit both ``(not x or not y or p)`` and
``(not x or not y or not p)``.  Together these two clauses are equivalent to
``(not x or not y)`` for any value of ``p``: if ``x`` and ``y`` are both true
they reduce to ``p`` and ``not p`` (unsatisfiable), otherwise one of the
negated literals is already true and both clauses hold regardless of ``p``.
Because ``p`` cancels out, a single shared fresh variable suffices for the
whole formula.

Each source clause therefore becomes 1 + 3*2 = 7 target clauses, and the
target uses ``num_vars + 1`` variables, so the reduction is linear time and
size.
"""

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an equisatisfiable 3-SAT instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[a, b, c], ...]}`` with
    positive literals only.  The result is a valid 3-SAT instance
    ``{"num_vars": m + 1, "clauses": [...]}``.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One global fresh variable used to pad the 2-literal "at most one"
    # constraints into 3-literal clauses.  It never appears in the source.
    pad = num_vars + 1

    result_clauses: list[list[int]] = []
    for a, b, c in clauses:
        # At least one of the three variables is true.
        result_clauses.append([a, b, c])
        # At most one of the three variables is true: for every pair (x, y)
        # add both padded versions of (not x or not y).
        for x, y in ((a, b), (a, c), (b, c)):
            result_clauses.append([-x, -y, pad])
            result_clauses.append([-x, -y, -pad])

    return {"num_vars": num_vars + 1, "clauses": result_clauses}
