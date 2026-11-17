"""Polynomial-time reduction from 1-in-3-SAT (SOURCE) to 3-SAT (TARGET).

A 1-in-3-SAT clause (a, b, c) is satisfied iff EXACTLY ONE of a, b, c is
true.  This is the conjunction of:

    at least one:  (a v b v c)
    at most one:   (not a v not b), (not a v not c), (not b v not c)

The "at least one" clause is already a legal 3-clause.  Each 2-literal
"at most one" clause is padded to three literals with a fresh variable F
that is forced to be false.  Since F is false, (not a v not b v F) is
equivalent to (not a v not b).

F is forced false with two fresh auxiliary variables x, y and the four
clauses:

    (not F v x v y), (not F v x v not y),
    (not F v not x v y), (not F v not x v not y)

If F were true these four clauses would require all four combinations of
x and y to satisfy (x v y), (x v not y), (not x v y), (not x v not y),
which is impossible.  Hence F must be false.

The reduction is linear in the size of the input (4 clauses per source
clause plus a constant-size gadget), so it runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: the source is trivially yes and so is the empty target.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    # Fresh variables: F is forced false; x, y are the forcing auxiliaries.
    false_var = num_vars + 1
    x = num_vars + 2
    y = num_vars + 3

    out_clauses: list[list[int]] = []

    # Force false_var to be false.
    out_clauses.append([-false_var, x, y])
    out_clauses.append([-false_var, x, -y])
    out_clauses.append([-false_var, -x, y])
    out_clauses.append([-false_var, -x, -y])

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])
        # At most one of a, b, c is true (padded with the false variable).
        out_clauses.append([-a, -b, false_var])
        out_clauses.append([-a, -c, false_var])
        out_clauses.append([-b, -c, false_var])

    return {"num_vars": num_vars + 3, "clauses": out_clauses}
