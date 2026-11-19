"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (standard "digit / big integer" reduction)
-------------------------------------------------------
Let the formula have m variables and n clauses.  We use base B = 10 and
numbers with m + n "digits":

  * digit i          (0 <= i < m)   corresponds to variable i+1
  * digit m + j      (0 <= j < n)   corresponds to clause j

For every variable v (1..m) we add two numbers:
  * T_v : digit v-1 is 1; digit m+j is 1 for every clause j containing +v
  * F_v : digit v-1 is 1; digit m+j is 1 for every clause j containing -v

For every clause j we add two "slack" numbers, each having digit m+j = 1
and all other digits 0.

The target has digit i = 1 for every variable and digit m+j = 3 for every
clause.

Because every digit of every number is 0 or 1, the maximum digit sum is
3 (variables) + 2 (slack) = 5 < 10, so there are no carries and the
digits behave independently.

Reaching the target forces exactly one of {T_v, F_v} to be chosen for each
variable (the variable digit must be exactly 1).  For clause j the chosen
variable numbers contribute the number of true literals of that clause
under the induced assignment, and the two slack numbers contribute at
most 2.  The clause digit reaches 3 iff at least one literal is true.
Hence a subset summing to the target exists iff the formula is satisfiable.
"""

from __future__ import annotations

from typing import Any

BASE = 10


def _value(digits: dict[int, int]) -> int:
    """Build an integer from a {digit_position: digit_value} mapping."""
    value = 0
    for position, digit in digits.items():
        value += digit * (BASE ** position)
    return value


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    numbers: list[int] = []

    # One pair of numbers per variable.
    for var in range(1, num_vars + 1):
        true_digits: dict[int, int] = {var - 1: 1}
        false_digits: dict[int, int] = {var - 1: 1}
        for j, clause in enumerate(clauses):
            if var in clause:
                true_digits[num_vars + j] = 1
            if -var in clause:
                false_digits[num_vars + j] = 1
        numbers.append(_value(true_digits))
        numbers.append(_value(false_digits))

    # Two slack numbers per clause.
    for j in range(num_clauses):
        numbers.append(_value({num_vars + j: 1}))
        numbers.append(_value({num_vars + j: 1}))

    # Target: 1 per variable digit, 3 per clause digit.
    target_digits: dict[int, int] = {i: 1 for i in range(num_vars)}
    for j in range(num_clauses):
        target_digits[num_vars + j] = 3
    target = _value(target_digits)

    return {"numbers": numbers, "target": target}
