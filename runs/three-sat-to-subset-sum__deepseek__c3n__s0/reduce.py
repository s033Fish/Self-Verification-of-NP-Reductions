"""Polynomial-time reduction from 3-SAT (SOURCE) to Subset Sum (TARGET).

Construction
------------
Work in base 10 (no carries occur because every column sum is < 10).
There are n = num_vars "variable" digit positions (0 .. n-1) and
k = len(clauses) "clause" digit positions (n .. n+k-1).

For each variable i (1-indexed) we add two numbers:
  * pos_i : digit 1 in variable position i-1, and digit 1 in the clause
            position of every clause that contains the literal +i.
  * neg_i : digit 1 in variable position i-1, and digit 1 in the clause
            position of every clause that contains the literal -i.

For each clause j we add two "filler" numbers:
  * 1 in clause position n+j
  * 2 in clause position n+j

The target has digit 1 in every variable position and digit 4 in every
clause position.

Correctness
-----------
Variable position i receives a contribution only from pos_i and neg_i,
each contributing 1, so the target forces exactly one of them to be
chosen -- i.e. a truth value for variable i.

For clause j, let c_j in {0,1,2,3} be the number of chosen literals that
satisfy clause j (contribution to that column). The two filler numbers
can contribute any s in {0,1,2,3} (subsets of {1,2}). The column must sum
to 4, so c_j + s = 4. Since s <= 3 this forces c_j >= 1: clause j is
satisfied. Conversely, if an assignment satisfies every clause then
c_j in {1,2,3} and s = 4 - c_j in {1,2,3} is realisable, so the target
is reachable. Hence the reduction is answer-preserving.

The construction uses O(n + k) numbers, each with O(n + k) digits, so it
runs in polynomial time.
"""

from __future__ import annotations

from typing import Any

BASE = 10


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = num_vars
    k = len(clauses)

    # Target: 1 in each variable column, 4 in each clause column.
    target = 0
    for i in range(n):
        target += BASE ** i
    for j in range(k):
        target += 4 * BASE ** (n + j)

    numbers: list[int] = []

    # One number per (variable, polarity).
    for i in range(1, n + 1):
        pos = BASE ** (i - 1)
        neg = BASE ** (i - 1)
        for j, clause in enumerate(clauses):
            if i in clause:
                pos += BASE ** (n + j)
            if -i in clause:
                neg += BASE ** (n + j)
        numbers.append(pos)
        numbers.append(neg)

    # Two filler numbers per clause.
    for j in range(k):
        numbers.append(BASE ** (n + j))
        numbers.append(2 * BASE ** (n + j))

    return {"numbers": numbers, "target": target}
