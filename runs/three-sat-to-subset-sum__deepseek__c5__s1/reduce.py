"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (standard digit/column encoding):

Let n = num_vars and k = len(clauses).  Work in base 10 with n + k digit
columns:

  * column i-1 (i = 1..n)  is the "variable column" of variable i,
  * column n+j (j = 0..k-1) is the "clause column" of clause j.

For every variable i we create two numbers:

  v_i  = 10^(i-1) + sum over clauses j where literal +i occurs of 10^(n+j)
  w_i  = 10^(i-1) + sum over clauses j where literal -i occurs of 10^(n+j)

For every clause j we create two slack numbers:

  s_j  = 10^(n+j)
  s'_j = 10^(n+j)

The target is

  t = sum_{i=1..n} 10^(i-1)  +  3 * sum_{j=0..k-1} 10^(n+j)

Correctness: choosing exactly one of {v_i, w_i} per variable puts a 1 in
variable column i (the only way to reach the required 1 there, since all
other numbers have 0 in that column).  In clause column j the chosen
variable numbers contribute exactly the number of true literals of clause
j (0..3), and the two slacks contribute 0, 1 or 2.  The column total can
reach exactly 3 iff at least one literal of the clause is true.  No digit
ever exceeds 3 + 2 = 5 < 10, so there are no carries between columns.

The construction is O((n+k)^2) digits, hence polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = num_vars
    k = len(clauses)

    numbers: list[int] = []

    # Variable numbers.
    for i in range(1, n + 1):
        var_col = 10 ** (i - 1)
        pos = var_col
        neg = var_col
        for j, clause in enumerate(clauses):
            col = 10 ** (n + j)
            if i in clause:
                pos += col
            if -i in clause:
                neg += col
        numbers.append(pos)
        numbers.append(neg)

    # Slack numbers, two per clause.
    for j in range(k):
        col = 10 ** (n + j)
        numbers.append(col)
        numbers.append(col)

    target = sum(10 ** (i - 1) for i in range(1, n + 1))
    target += 3 * sum(10 ** (n + j) for j in range(k))

    return {"numbers": numbers, "target": target}
