"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Idea
----
Standard chain: 3-SAT -> NAE-4-SAT -> NAE-3-SAT.

Step 1 (3-SAT -> NAE-4-SAT): introduce one fresh global variable z and map
every clause C = [l1, l2, l3] to the 4-literal NAE clause [l1, l2, l3, z].
If the 3-SAT formula is satisfiable, set z = false; then every clause has a
true literal and z is false, so it is not all-equal.  Conversely, if the NAE
formula is satisfiable, complementing all variables (which preserves NAE)
gives a satisfying assignment with z = false, and then every clause must
contain a true literal, i.e. the 3-SAT formula is satisfiable.

Step 2 (NAE-4-SAT -> NAE-3-SAT): replace each 4-literal NAE clause
[a, b, c, d] by two 3-literal NAE clauses [a, b, y] and [-y, c, d] using a
fresh variable y.  One checks that the pair is satisfiable (over y) exactly
when a, b, c, d are not all equal.

Combining: for each source clause [l1, l2, l3] with fresh variable y_i we emit
[l1, l2, y_i] and [-y_i, l3, z].

The result uses num_vars + 1 + len(clauses) variables and 2 * len(clauses)
clauses, so the reduction is linear time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    z = num_vars + 1  # global "truth" variable, set to false in the forward direction
    new_clauses: list[list[int]] = []

    for i, clause in enumerate(clauses):
        y = num_vars + 2 + i  # fresh variable for this clause
        l1, l2, l3 = clause
        new_clauses.append([l1, l2, y])
        new_clauses.append([-y, l3, z])

    return {
        "num_vars": num_vars + 1 + len(clauses),
        "clauses": new_clauses,
    }
