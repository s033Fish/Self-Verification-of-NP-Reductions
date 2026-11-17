"""Reduction from 1-in-3-SAT (positive literals) to 3-SAT.

The source problem (OneInThreeSat) expects clauses of three *positive* variables
and is satisfied when exactly one variable in each clause is true.

We transform each source clause (x ∨ y ∨ z) into a set of 3‑SAT clauses that
enforce the same condition:

  * At least one of x, y, z is true:   ( x  ∨  y  ∨  z )
  * At most one is true, i.e. for every pair (p,q): ¬p ∨ ¬q.

The “at most one” constraints are binary clauses.  3‑SAT requires exactly three
different literals per clause, so we introduce a fresh auxiliary variable *d*
for each original clause and replace each binary clause by the pair:

    ( ¬p ∨ ¬q ∨  d )
    ( ¬p ∨ ¬q ∨ ¬d )

Both clauses are satisfied iff ¬p ∨ ¬q holds, because the auxiliary variable can
be assigned arbitrarily; the two clauses together force it to be both true and
false otherwise, which is impossible.

Thus each source clause yields seven 3‑SAT clauses and one new variable.  The
reduction runs in linear time in the size of the input.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    The returned instance satisfies the format required by ``ThreeSat``:
    ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each clause
    contains three *different* literals on three distinct variables.

    The reduction preserves satisfiability: the target instance is satisfiable
    iff the source instance has an assignment with exactly one true variable in
    every clause.
    """
    # Basic validation of structure.
    if not isinstance(instance, dict):
        raise ValueError("instance must be a dict")
    if set(instance.keys()) != {"num_vars", "clauses"}:
        raise ValueError("instance must have keys 'num_vars' and 'clauses'")

    m: int = int(instance["num_vars"])  # original number of variables
    source_clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses – trivially yes.  3‑SAT with no clauses is also
    # trivially satisfiable.
    if not source_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses: List[List[int]] = []
    next_var = m  # will be incremented for each auxiliary variable

    for clause in source_clauses:
        if len(clause) != 3:
            raise ValueError("Each source clause must contain exactly three variables")
        a, b, c = clause
        # Clause enforcing at least one true literal.
        new_clauses.append([a, b, c])

        # Fresh auxiliary variable for this original clause.
        next_var += 1
        d = next_var

        # Helper to add the pair of 3‑literal clauses for a binary constraint.
        def add_pair(p: int, q: int) -> None:
            new_clauses.append([-p, -q, d])
            new_clauses.append([-p, -q, -d])

        add_pair(a, b)
        add_pair(a, c)
        add_pair(b, c)

    return {"num_vars": next_var, "clauses": new_clauses}

