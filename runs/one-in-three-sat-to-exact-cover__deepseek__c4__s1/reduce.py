"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

SOURCE: OneInThreeSat  {"num_vars": m, "clauses": [[a,b,c], ...]}
TARGET: ExactCover     {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Universe elements:
  * for each variable i in 1..m : element (i-1)          (the "variable" element)
  * for each clause  j          : element (m + j)        (the "clause" element)

Sets:
  * for each variable i:
      T_i = [i-1] + [m + j for every clause j containing variable i]
      F_i = [i-1]

Both T_i and F_i contain the variable element (i-1), so at most one of them
can be selected, and since that element must be covered, exactly one is
selected.  Selecting T_i means "x_i is true".  The clause element m+j lies in
exactly the sets T_i for i in clause j, so it is covered exactly once iff
exactly one variable of clause j is set true.  Hence exact covers correspond
bijectively to assignments with exactly one true variable per clause.

Edge cases: m = 0 and no clauses -> universe_size 0, no sets -> yes.
Variables that occur in no clause yield T_i = F_i = [i-1] (duplicate sets),
which is harmless.
"""

from __future__ import annotations


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # clause_of_var[i] = list of clause indices (0-based) containing variable i+1
    clause_of_var = [[] for _ in range(num_vars)]
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_of_var[var - 1].append(j)

    universe_size = num_vars + len(clauses)

    sets = []
    for i in range(num_vars):
        var_element = i
        true_set = [var_element] + [num_vars + j for j in clause_of_var[i]]
        false_set = [var_element]
        sets.append(true_set)
        sets.append(false_set)

    return {"universe_size": universe_size, "sets": sets}
