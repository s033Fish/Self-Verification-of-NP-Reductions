"""Polynomial-time reduction from 1-in-3-SAT (positive) to Subset Sum.

Encoding
--------
Let m = num_vars and n = len(clauses).  Work in base B = 4.

Digit positions:
  * positions 0 .. m-1      -> one "variable digit" per variable
  * positions m .. m+n-1    -> one "clause digit" per clause

For each variable i (1-based, so digit index i-1) create two numbers:
  T_i = B^(i-1) + sum over clauses j (0-based) that contain i of B^(m+j)
  F_i = B^(i-1)

Target:
  sum_{i=0}^{m-1} B^i  +  sum_{j=0}^{n-1} B^(m+j)

Why it works
------------
Every number has variable digit in {0,1} and clause digits in {0,1}.
In any selection each digit sum is at most 2 (variable digit, from T_i+F_i)
or at most 3 (clause digit, from T_a+T_b+T_c), both < B = 4, so there are
no carries between digit positions.

Variable digit i must equal 1, and only T_i and F_i have a nonzero entry
there, so exactly one of {T_i, F_i} is chosen -> a well-defined assignment.
Clause digit j must equal 1, and it receives 1 exactly from each chosen T
of a variable appearing in clause j, so exactly one variable of clause j is
true.  Hence a subset summing to the target exists iff the formula is
1-in-3 satisfiable.  The construction is linear in the input size.
"""

from __future__ import annotations

BASE = 4


def reduce(instance):
    """Reduce a positive 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # clause_occurrences[i] = list of clause indices (0-based) containing var i+1
    clause_occurrences = [[] for _ in range(num_vars)]
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_occurrences[var - 1].append(j)

    numbers = []
    for i in range(num_vars):
        var_digit = BASE ** i
        true_value = var_digit
        for j in clause_occurrences[i]:
            true_value += BASE ** (num_vars + j)
        numbers.append(true_value)   # T_i : variable i is true
        numbers.append(var_digit)    # F_i : variable i is false

    target = sum(BASE ** i for i in range(num_vars))
    target += sum(BASE ** (num_vars + j) for j in range(n))

    return {"numbers": numbers, "target": target}
