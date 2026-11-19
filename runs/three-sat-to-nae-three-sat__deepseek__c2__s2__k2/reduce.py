"""Polynomial-time reduction from 3-SAT (SOURCE) to NAE-3-SAT (TARGET).

Construction
------------
Given a 3-SAT instance with variables 1..m and clauses C_1..C_k, introduce
one global variable g = m+1 and, for each clause C_i = (l1 v l2 v l3), a
fresh variable y_i.  Replace C_i by the two NAE-3 clauses

    NAE(l1, l2, y_i)        and        NAE(~y_i, l3, g).

Correctness
-----------
(=>) If an assignment sigma satisfies the 3-SAT formula, set g = false.
    For a clause with l3 true, NAE(~y_i, l3, false) holds for every y_i, and
    y_i can be chosen to make NAE(l1, l2, y_i) hold (choose y_i = ~l1 when
    l1 = l2, arbitrary otherwise).  For a clause with l3 false, l1 v l2 must
    hold, so y_i = false satisfies NAE(~y_i, false, false) and makes
    NAE(l1, l2, false) hold.  Hence the NAE instance is satisfiable.

(<=) NAE-3-SAT is invariant under complementing every variable (flipping all
    literals preserves "not all equal").  So if the NAE instance has any
    satisfying assignment, it also has one with g = false.  With g = false,
    NAE(~y_i, l3, false) forces y_i = false whenever l3 is false, and then
    NAE(l1, l2, false) forces l1 v l2.  Thus every original clause is
    satisfied, so the 3-SAT instance is satisfiable.

The construction is linear in the input size, hence polynomial time.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance (same yes/no answer)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    if not clauses:
        # A clause-free formula is yes for both problems; keep it clause-free.
        return {"num_vars": num_vars, "clauses": []}

    global_var = num_vars + 1
    next_var = global_var + 1
    new_clauses: list[list[int]] = []

    for clause in clauses:
        l1, l2, l3 = clause
        y = next_var
        next_var += 1
        new_clauses.append([l1, l2, y])
        new_clauses.append([-y, l3, global_var])

    return {"num_vars": next_var - 1, "clauses": new_clauses}
