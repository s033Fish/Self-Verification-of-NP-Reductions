"""Polynomial-time reduction from 3-SAT (ThreeSat) to Subset Sum (SubsetSum).

Standard digit-encoding reduction.

Let n = num_vars and k = num_clauses.  Work in base 10 with n + k digit
positions: one position per variable and one position per clause.

For every variable v (1..n) we add two numbers:
  * T_v: digit 1 in variable-position v, and digit 1 in the clause-position
    of every clause in which +v occurs.
  * F_v: digit 1 in variable-position v, and digit 1 in the clause-position
    of every clause in which -v occurs.

For every clause c we add two "slack" numbers, each having digit 1 in the
clause-position of c (and 0 elsewhere).

The target has digit 1 in every variable-position and digit 3 in every
clause-position.

Because no clause position ever accumulates more than 3 (literals) + 2
(slacks) = 5 < 10, there are no carries between positions.

* The variable-position target of 1 forces exactly one of T_v / F_v to be
  chosen, which encodes a truth assignment.
* A clause-position can reach 3 only if at least one of its three literals is
  true (the two slacks contribute at most 2), so every clause must be
  satisfied.

Hence the subset sums to the target iff the formula is satisfiable.
"""

from __future__ import annotations

from typing import Any

BASE = 10


def _pack(digits: list[int]) -> int:
    """Interpret ``digits`` (least significant first) as a base-BASE number."""
    value = 0
    for d in reversed(digits):
        value = value * BASE + d
    return value


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Position layout (least significant first): clauses 0..k-1, then
    # variables 0..n-1.
    total = num_vars + num_clauses

    def position(kind: str, index: int) -> int:
        if kind == "clause":
            return index
        return num_clauses + index

    numbers: list[int] = []

    # Variable numbers.
    for v in range(1, num_vars + 1):
        pos_digits = [0] * total
        neg_digits = [0] * total
        pos_digits[position("var", v - 1)] = 1
        neg_digits[position("var", v - 1)] = 1
        for c_index, clause in enumerate(clauses):
            if v in clause:
                pos_digits[position("clause", c_index)] = 1
            if -v in clause:
                neg_digits[position("clause", c_index)] = 1
        numbers.append(_pack(pos_digits))
        numbers.append(_pack(neg_digits))

    # Two slack numbers per clause.
    for c_index in range(num_clauses):
        slack_digits = [0] * total
        slack_digits[position("clause", c_index)] = 1
        slack = _pack(slack_digits)
        numbers.append(slack)
        numbers.append(slack)

    # Target: 1 per variable position, 3 per clause position.
    target_digits = [0] * total
    for v in range(num_vars):
        target_digits[position("var", v)] = 1
    for c_index in range(num_clauses):
        target_digits[position("clause", c_index)] = 3
    target = _pack(target_digits)

    return {"numbers": numbers, "target": target}
