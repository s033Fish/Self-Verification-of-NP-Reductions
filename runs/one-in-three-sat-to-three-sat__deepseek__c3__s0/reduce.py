"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

SOURCE = OneInThreeSat: positive clauses (a, b, c); yes iff some assignment
makes EXACTLY ONE of a, b, c true in every clause.

TARGET = ThreeSat: clauses of exactly 3 literals on 3 distinct variables;
yes iff some assignment satisfies every clause.

Construction
------------
For each source clause (a, b, c), "exactly one of a, b, c is true" is the
conjunction of:

    (a or b or c)                     # at least one true
    (not a or not b)                  # at most one true
    (not a or not c)
    (not b or not c)

The first clause is already a legal 3-SAT clause.  Each 2-literal clause
(u or v) is replaced by the pair

    (u or v or x), (u or v or not x)

which is satisfiable for a fixed x exactly when (u or v) is: if u or v holds,
one of the two clauses is satisfied regardless of x; if neither holds, the two
clauses demand x and not x simultaneously.  A single fresh variable x = m + 1
can be reused for every padding pair, since the pairs are independent.

The result uses m + 1 variables and at most 4 clauses per source clause, so
the reduction is linear time and size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    fresh = num_vars + 1  # a single fresh variable used for all padding

    target_clauses: list[list[int]] = []
    for a, b, c in clauses:
        # At least one of a, b, c is true (already 3 distinct variables).
        target_clauses.append([a, b, c])
        # At most one of a, b, c is true, padded to length 3 with `fresh`.
        for u, v in ((a, b), (a, c), (b, c)):
            target_clauses.append([-u, -v, fresh])
            target_clauses.append([-u, -v, -fresh])

    return {"num_vars": fresh, "clauses": target_clauses}
