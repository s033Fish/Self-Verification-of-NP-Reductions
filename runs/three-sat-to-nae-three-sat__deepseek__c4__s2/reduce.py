"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Given a 3-SAT instance with m variables and clauses C_1..C_k, we build a
NAE-3-SAT instance as follows.

Let s = m+1 be a fresh global "base" variable.  For each clause
C_i = (l1 v l2 v l3) introduce a fresh variable y_i and emit the two
NAE-3 clauses

    NAE(l1, l2,  y_i)
    NAE(l3,  s, -y_i)

Correctness
-----------
(=>) If the 3-SAT formula is satisfiable, take a satisfying assignment and
set s = false.  For a clause C_i:
  * if l1 or l2 is true, set y_i = false: (l1,l2,false) is not all equal and
    (l3,false,true) is not all equal.
  * otherwise l3 is true; set y_i = true: (false,false,true) is not all equal
    and (true,false,false) is not all equal.
So every NAE clause holds.

(<=) If the NAE formula is satisfiable, NAE is invariant under complementing
all variables (flipping every truth value keeps "not all equal" true), so we
may assume s = false.  For a clause C_i:
  * if y_i = false then NAE(l1,l2,false) forces l1 v l2 to be true;
  * if y_i = true then NAE(l3,false,false) forces l3 to be true.
Either way C_i is satisfied.  Hence the 3-SAT formula is satisfiable.

The construction is linear in the input size, so it runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    k = len(clauses)
    base = num_vars + 1  # the global base variable s

    new_clauses = []
    for i, clause in enumerate(clauses):
        l1, l2, l3 = clause
        y = num_vars + 2 + i  # fresh auxiliary variable for this clause
        new_clauses.append([l1, l2, y])
        new_clauses.append([l3, base, -y])

    return {"num_vars": num_vars + 1 + k, "clauses": new_clauses}
