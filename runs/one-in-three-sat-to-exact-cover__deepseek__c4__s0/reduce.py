"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Construction
------------
Let the source instance have variables 1..m and clauses C_1..C_t, where
clause C_j = [a, b, c] (three distinct positive variables).

Elements (the universe):
  * e_x                for every variable x in 1..m
  * T[j][p], F[j][p]   for every clause j and position p in {0,1,2}

Variable gadget (for each variable x):
  * set  { e_x } U { T[j][p] : variable at (j,p) is x }
  * set  { e_x } U { F[j][p] : variable at (j,p) is x }

  Exactly one of the two sets must be chosen because e_x occurs only in
  them.  Choosing the T-set means "x is true" and covers every T-copy of
  x; choosing the F-set means "x is false" and covers every F-copy.

Clause gadget (for each clause j = [a,b,c] with positions 0,1,2):
  * { F[j][0], T[j][1], T[j][2] }   (a true, b false, c false)
  * { T[j][0], F[j][1], T[j][2] }   (b true, a false, c false)
  * { T[j][0], T[j][1], F[j][2] }   (c true, a false, b false)

  F[j][0] appears only in the first set, F[j][1] only in the second and
  F[j][2] only in the third.  The variable gadget covers exactly one of
  T[j][p] / F[j][p] for each p, so the uncovered copy of each position
  must be covered by a clause set.  This forces exactly one of the three
  sets to be chosen, i.e. exactly one of a, b, c to be true.

The construction uses O(m + t) elements and sets, so it is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_id = 0

    # One element per variable.
    var_elem: dict[int, int] = {}
    for x in range(1, num_vars + 1):
        var_elem[x] = next_id
        next_id += 1

    # Two occurrence elements (T and F) per clause position.
    t_elem: dict[tuple[int, int], int] = {}
    f_elem: dict[tuple[int, int], int] = {}
    for j, clause in enumerate(clauses):
        for p in range(3):
            t_elem[(j, p)] = next_id
            next_id += 1
            f_elem[(j, p)] = next_id
            next_id += 1

    universe_size = next_id
    sets: list[list[int]] = []

    # Variable gadgets.
    for x in range(1, num_vars + 1):
        t_copies = [
            t_elem[(j, p)]
            for j, clause in enumerate(clauses)
            for p in range(3)
            if clause[p] == x
        ]
        f_copies = [
            f_elem[(j, p)]
            for j, clause in enumerate(clauses)
            for p in range(3)
            if clause[p] == x
        ]
        sets.append([var_elem[x]] + t_copies)
        sets.append([var_elem[x]] + f_copies)

    # Clause gadgets.
    for j in range(len(clauses)):
        sets.append([f_elem[(j, 0)], t_elem[(j, 1)], t_elem[(j, 2)]])
        sets.append([t_elem[(j, 0)], f_elem[(j, 1)], t_elem[(j, 2)]])
        sets.append([t_elem[(j, 0)], t_elem[(j, 1)], f_elem[(j, 2)]])

    return {"universe_size": universe_size, "sets": sets}
