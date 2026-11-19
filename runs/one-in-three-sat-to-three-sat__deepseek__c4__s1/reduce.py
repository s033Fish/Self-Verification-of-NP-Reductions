"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

SOURCE: OneInThreeSat (positive 1-in-3-SAT).
TARGET: ThreeSat (3-SAT).

Idea
----
A 1-in-3 clause (a, b, c) means "exactly one of a, b, c is true", which is
equivalent to the conjunction of:

    at least one:  (a or b or c)
    at most one:   (not a or not b), (not a or not c), (not b or not c)

The target requires exactly 3 literals per clause on 3 different variables,
so each 2-literal "at most one" clause (not x or not y) is padded with a
fresh dummy variable d into the two 3-literal clauses:

    (not x or not y or d)
    (not x or not y or not d)

For any fixed value of d exactly one of these two clauses reduces to
(not x or not y); together they are satisfiable (over x, y, d) iff
(not x or not y) holds.  A single fresh dummy variable d = m + 1 is shared
by all padded clauses, which is sound because the argument holds for every
value of d independently of the other clauses.

Thus the constructed 3-SAT instance is satisfiable iff the original
1-in-3-SAT instance is.  The construction uses O(#clauses) clauses and one
extra variable, so it runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: both problems are trivially yes, keep the variable count.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    # Fresh dummy variable, guaranteed not to clash with 1..num_vars.
    dummy = num_vars + 1

    out_clauses: list[list[int]] = []
    for a, b, c in clauses:
        # At least one of the three is true.
        out_clauses.append([a, b, c])
        # At most one: for each pair, forbid both being true.
        for x, y in ((a, b), (a, c), (b, c)):
            out_clauses.append([-x, -y, dummy])
            out_clauses.append([-x, -y, -dummy])

    return {"num_vars": dummy, "clauses": out_clauses}
