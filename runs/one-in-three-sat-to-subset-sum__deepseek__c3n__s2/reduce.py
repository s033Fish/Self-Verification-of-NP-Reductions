"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Encoding
--------
Fix a base B (we use B = 4).  We use one digit position per variable and one
digit position per clause:

    variable i (1..m)  ->  position i-1
    clause   j         ->  position m+j

For every variable i we create two numbers:

    T_i : digit 1 in variable-position i-1, and digit 1 in the clause-position
          of every clause that contains variable i.
    F_i : digit 1 in variable-position i-1 only.

The target has digit 1 in every position (variable and clause positions).

Why it works
------------
Because B = 4 is larger than any possible digit sum (a variable position is
touched by exactly two numbers, a clause position by at most three numbers),
there are no carries: a subset sums to the target iff its digit vector equals
the all-ones vector.

* At variable-position i-1 only T_i and F_i have a 1, so the subset must
  contain exactly one of them.  This models a truth assignment (T_i = true,
  F_i = false).
* At clause-position m+j the digit equals the number of chosen T_i for
  variables i appearing in clause j, i.e. the number of true variables in
  that clause.  Equality with 1 therefore enforces "exactly one true variable
  per clause".

Hence the produced Subset Sum instance is yes iff the 1-in-3-SAT instance is
yes.  The construction is clearly polynomial in the input size.
"""

from __future__ import annotations

from typing import Any

BASE = 4


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Positions: 0..num_vars-1 for variables, num_vars..num_vars+num_clauses-1
    # for clauses.
    total_positions = num_vars + num_clauses

    target = 0
    for pos in range(total_positions):
        target += BASE ** pos

    # For each variable, collect the clause positions it occurs in.
    var_clause_positions: list[list[int]] = [[] for _ in range(num_vars + 1)]
    for j, clause in enumerate(clauses):
        for var in clause:
            var_clause_positions[var].append(num_vars + j)

    numbers: list[int] = []
    for var in range(1, num_vars + 1):
        var_pos = var - 1
        true_number = BASE ** var_pos
        for pos in var_clause_positions[var]:
            true_number += BASE ** pos
        false_number = BASE ** var_pos
        numbers.append(true_number)
        numbers.append(false_number)

    return {"numbers": numbers, "target": target}
