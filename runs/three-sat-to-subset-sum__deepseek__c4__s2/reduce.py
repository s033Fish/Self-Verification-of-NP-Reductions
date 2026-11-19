"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (standard digit / base-10 encoding):

Let the formula have n variables and k clauses.  Use numbers whose decimal
digits are split into k "clause" digits (positions 0..k-1) and n "variable"
digits (positions k..k+n-1).  All digits stay < 10 so there are no carries.

For every variable i (1..n) add two numbers:
    v_i  : 1 in variable digit i, plus 1 in clause digit j for each clause j
           in which +i occurs.
    v'_i : 1 in variable digit i, plus 1 in clause digit j for each clause j
           in which -i occurs.

For every clause j add two "slack" numbers:
    s_j  = 1 in clause digit j
    s'_j = 2 in clause digit j

Target: 1 in every variable digit and 4 in every clause digit.

Choosing exactly one of {v_i, v'_i} sets each variable digit to 1 and makes
clause digit j equal to t_j, the number of true literals in clause j (0..3).
The slack pair s_j/s'_j can contribute 0, 1, 2 or 3 to clause digit j, so the
digit can be brought up to 4 iff t_j >= 1 (if t_j = 0 the most the slacks can
add is 3 < 4).  Hence a satisfying assignment gives a subset summing to the
target, and any subset summing to the target must pick exactly one
literal-number per variable and have t_j >= 1 for every clause, i.e. it
encodes a satisfying assignment.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = num_vars
    k = len(clauses)

    numbers: list[int] = []

    # One number per literal of each variable.
    for i in range(1, n + 1):
        pos = 10 ** (k + i - 1)
        neg = 10 ** (k + i - 1)
        for j, clause in enumerate(clauses):
            if i in clause:
                pos += 10 ** j
            if -i in clause:
                neg += 10 ** j
        numbers.append(pos)
        numbers.append(neg)

    # Slack numbers for each clause.
    for j in range(k):
        numbers.append(10 ** j)
        numbers.append(2 * 10 ** j)

    # Target: variable digits all 1, clause digits all 4.
    target = sum(10 ** (k + i) for i in range(n)) + 4 * sum(10 ** j for j in range(k))

    return {"numbers": numbers, "target": target}
