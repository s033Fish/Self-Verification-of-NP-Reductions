"""Polynomial-time reduction from 1-in-3-SAT (positive) to Exact Cover.

SOURCE: {"num_vars": m, "clauses": [[a, b, c], ...]}  (positive, distinct vars)
TARGET: {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Universe elements:
  * v_i  (element i-1)          for each variable i = 1..m
  * c_j  (element m + j)        for each clause j = 0..n-1

Sets:
  * A_i = [v_i] + [c_j for every clause j containing variable i]   ("i is true")
  * B_i = [v_i]                                                    ("i is false")

Exactly one of A_i, B_i must be chosen (both contain v_i, and v_i must be
covered).  Choosing A_i means variable i is true and it covers every clause
element c_j for clauses containing i.  A clause element c_j can only be
covered by A_i for i in clause j, and it must be covered exactly once, so
exactly one variable of each clause is true.  Hence exact covers correspond
exactly to 1-in-3 satisfying assignments.
"""

from __future__ import annotations

from problems import SOURCE, TARGET


def reduce(instance: dict) -> dict:
    SOURCE.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    universe_size = num_vars + n
    sets: list[list[int]] = []

    for var in range(1, num_vars + 1):
        var_element = var - 1
        true_set = [var_element]
        for j, clause in enumerate(clauses):
            if var in clause:
                true_set.append(num_vars + j)
        sets.append(true_set)      # A_var : variable is true
        sets.append([var_element])  # B_var : variable is false

    result = {"universe_size": universe_size, "sets": sets}
    TARGET.validate(result)
    return result
