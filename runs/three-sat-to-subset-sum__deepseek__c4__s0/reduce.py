"""Polynomial-time reduction from 3-SAT (SOURCE) to Subset Sum (TARGET).

Construction
------------
Let the formula have n = num_vars variables and k = len(clauses) clauses.
We use base-10 positional notation with n + k digits:

  * digit i        (0 <= i < n)  encodes variable i+1
  * digit n + j    (0 <= j < k)  encodes clause j

For every variable v = i+1 we add two numbers:

  pos_v = 10^i + sum(10^(n+j) for each clause j containing literal  +v)
  neg_v = 10^i + sum(10^(n+j) for each clause j containing literal  -v)

For every clause j we add two identical "slack" numbers:

  slack_j = 10^(n+j)          (added twice)

Target:

  T = sum(10^i for i in 0..n-1) + 3 * sum(10^(n+j) for j in 0..k-1)

Correctness
-----------
Every digit position receives at most 3 (literals) + 2 (slacks) = 5 < 10, so
there are no carries between digits.

Variable digit i: only pos_v and neg_v contribute (each 1).  The target digit
is 1, so any solution selects exactly one of the pair -> a truth assignment.

Clause digit j: let t_j be the number of selected literal-numbers whose
literal occurs in clause j (i.e. the number of true literals in clause j).
The two slacks contribute 0, 1 or 2.  The digit must equal 3.

  * If the assignment satisfies clause j then t_j >= 1, and choosing slacks
    appropriately (2 if t_j == 1, 1 if t_j == 2, 0 if t_j == 3) gives 3.
  * If t_j == 0 the slacks contribute at most 2 < 3, so the digit cannot be
    reached.

Hence a subset sums to T iff the induced assignment satisfies every clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = num_vars
    k = len(clauses)

    # clause_pos[j] = positional weight of clause j
    clause_pos = [10 ** (n + j) for j in range(k)]

    numbers: list[int] = []

    # For each variable, find which clauses contain +v and -v.
    for v in range(1, n + 1):
        var_weight = 10 ** (v - 1)
        pos = var_weight
        neg = var_weight
        for j, clause in enumerate(clauses):
            if v in clause:
                pos += clause_pos[j]
            if -v in clause:
                neg += clause_pos[j]
        numbers.append(pos)
        numbers.append(neg)

    # Two slack numbers per clause.
    for j in range(k):
        numbers.append(clause_pos[j])
        numbers.append(clause_pos[j])

    target = sum(10 ** i for i in range(n)) + 3 * sum(clause_pos)

    return {"numbers": numbers, "target": target}
