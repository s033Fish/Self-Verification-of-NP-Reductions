"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Source instance (1-in-3-SAT):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    Variables are 1..m; each clause has 3 distinct positive variables.

Target instance (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Universe elements:
    * v_i  -> element index i-1          (one per variable, i = 1..m)
    * e_j  -> element index m + j        (one per clause, j = 0..k-1)

Sets:
    * For each variable i:
        T_i = [i-1] + [m+j for every clause j containing variable i]
              (represents "x_i is true"; also covers the clause elements of
               clauses in which x_i is the true literal)
        F_i = [i-1]
              (represents "x_i is false")
    * No other sets are needed: every clause element e_j is covered by the
      T-sets of the three variables in clause j.

Why it works
------------
Element v_i is contained only in T_i and F_i, so an exact cover must choose
exactly one of them: this encodes a total truth assignment (T_i chosen <=>
x_i true).  For a clause (a, b, c), element e_j is contained exactly in
T_a, T_b, T_c, so it is covered exactly once iff exactly one of T_a, T_b,
T_c is chosen, i.e. iff exactly one of a, b, c is true.  Hence exact covers
correspond bijectively to assignments making exactly one variable true in
every clause.

Edge cases: with no clauses the universe is just {v_1..v_m} and the sets are
T_i = F_i = {v_i}; an exact cover exists for every m (including m = 0, where
the universe is empty).  This matches 1-in-3-SAT being yes for clause-free
formulas.

The construction runs in O(m + total clause size) time, hence polynomial.
"""

from typing import Any


def reduce(instance: Any) -> dict:
    """Return an Exact Cover instance equivalent to the 1-in-3-SAT input."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Element index for variable i (1-based) is i - 1.
    # Element index for clause j (0-based) is num_vars + j.
    universe_size = num_vars + len(clauses)

    # For each variable, collect the clause elements it should cover when true.
    true_extra: list[list[int]] = [[] for _ in range(num_vars + 1)]
    for j, clause in enumerate(clauses):
        clause_element = num_vars + j
        for var in clause:
            true_extra[var].append(clause_element)

    sets: list[list[int]] = []
    for i in range(1, num_vars + 1):
        var_element = i - 1
        # T_i: variable is true, covers clause elements of clauses using i.
        sets.append([var_element] + true_extra[i])
        # F_i: variable is false.
        sets.append([var_element])

    return {"universe_size": universe_size, "sets": sets}
