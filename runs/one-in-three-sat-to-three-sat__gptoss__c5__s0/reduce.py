"""Reduction from 1-in-3 SAT (positive) to 3-SAT.

The source problem (OneInThreeSat) requires that in each clause exactly one
of the three variables is true.  The target problem (ThreeSat) requires that
each clause contains at least one true literal.

For a clause (a, b, c) we enforce the required condition with the following
3‑CNF gadget:

* At least one true: (a ∨ b ∨ c)
* At most one true: for each pair (x, y) we need (¬x ∨ ¬y).  A 2‑literal clause
  can be simulated with two 3‑literal clauses using a fresh auxiliary variable
  p:
      (¬x ∨ ¬y ∨  p)  and  (¬x ∨ ¬y ∨ ¬p)
  These two clauses are satisfied exactly when ¬x ∨ ¬y holds, because if both
  x and y were true the first clause forces p = true while the second forces
  p = false – impossible.

Putting the pieces together, each original clause yields seven 3‑literal
clauses and introduces three fresh auxiliary variables (one per pair).  The
construction runs in polynomial time and produces a valid ThreeSat instance
as required by ``benchmark/problems`` validation helpers.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import OneInThreeSat, ThreeSat


def _pairwise_constraints(x: int, y: int, aux_var: int) -> List[List[int]]:
    """Return the two 3‑SAT clauses that enforce (¬x ∨ ¬y) using aux_var.

    The clauses are ``[-x, -y,  aux_var]`` and ``[-x, -y, -aux_var]``.
    """
    return [[-x, -y, aux_var], [-x, -y, -aux_var]]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    The returned instance satisfies the validation rules of ``ThreeSat`` and
    is satisfiable iff the input instance is satisfiable under the exactly‑one
    condition.
    """
    # Validate the source instance first – will raise InvalidInstance on error.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # No clauses -> trivially satisfiable.  Preserve the number of variables.
    if not source_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses: List[List[int]] = []
    next_var: int = m + 1  # first fresh variable index

    for clause in source_clauses:
        a, b, c = clause  # each clause has exactly three distinct positive ints
        # At least one true
        new_clauses.append([a, b, c])

        # Pairwise at-most-one constraints, each introduces a fresh aux variable
        for x, y in ((a, b), (a, c), (b, c)):
            aux = next_var
            next_var += 1
            new_clauses.extend(_pairwise_constraints(x, y, aux))

    # Total number of variables after adding auxiliaries
    total_vars = next_var - 1
    # Validate the produced instance before returning.
    ThreeSat.validate({"num_vars": total_vars, "clauses": new_clauses})
    return {"num_vars": total_vars, "clauses": new_clauses}

