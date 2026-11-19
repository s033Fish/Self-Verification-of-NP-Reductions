"""Polynomial-time reduction from 3-SAT (ThreeSat) to NAE-3-SAT (NaeThreeSat).

Reduction idea
--------------
NAE-3-SAT is invariant under complementing *all* variables (flipping every
truth value turns a "not all equal" clause into another "not all equal"
clause).  Hence a gadget that is applied clause by clause cannot encode the
requirement "at least one literal is true" without an outside anchor: the
all-false assignment is always as good as the all-true one.

The standard fix is a single global anchor variable ``z``.  For a 3-SAT
clause ``(l1 or l2 or l3)`` consider the 4-literal NAE clause
``NAE(l1, l2, l3, z)``.  If ``z`` is false this says "not all of
l1, l2, l3 are false", i.e. exactly the original clause.  If ``z`` is true it
says "not all of l1, l2, l3 are true", which is weaker.  But the whole
formula is invariant under flipping all variables, so any satisfying
assignment with ``z = true`` can be flipped to one with ``z = false`` that
still satisfies every clause.  Therefore the formula is satisfiable iff the
original 3-SAT formula is.

It remains to express each 4-literal NAE clause with 3-literal NAE clauses.
The identity

    NAE(a, b, c, d)  <=>  exists y:  NAE(a, b, y) and NAE(c, d, not y)

is easily checked by case analysis (if a,b,c,d are not all equal, pick y
different from a; if they are all equal, no y works).  So we introduce one
fresh helper variable ``y`` per source clause and emit

    [l1, l2,  y]
    [l3,  z, -y]

Every emitted clause uses 3 distinct variables: ``l1, l2, l3`` are on
distinct variables, ``y`` is fresh, and ``z`` is a fresh variable distinct
from all of them.  The number of variables is m + 1 + (#clauses) and the
number of clauses is 2 * (#clauses), so the reduction is linear time.

Edge case: a source formula with no clauses reduces to a target formula with
no clauses, which is yes (and m + 1 variables are still allowed).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` with
    literals over variables ``1..m``.  The returned instance is a valid
    NAE-3-SAT instance that is satisfiable iff ``instance`` is.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # z is the global anchor variable; helper variables follow it.
    z = num_vars + 1
    next_var = z + 1

    new_clauses: list[list[int]] = []
    for l1, l2, l3 in clauses:
        helper = next_var
        next_var += 1
        # NAE(l1, l2, helper) and NAE(l3, z, not helper)
        new_clauses.append([l1, l2, helper])
        new_clauses.append([l3, z, -helper])

    return {"num_vars": next_var - 1, "clauses": new_clauses}
