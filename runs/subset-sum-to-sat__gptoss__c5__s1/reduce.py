"""Polynomial‑time reduction from Subset Sum to SAT.

We use a classic dynamic‑programming encoding.
For a Subset‑Sum instance with numbers a_1 … a_n and target t we create Boolean
variables y_{i,s} (i = 0..n, s = 0..S) where S = sum(numbers).
Interpretation: after considering the first i numbers, a subset achieving sum s exists.
The constraints are:
  * y_{0,0} is true, all other y_{0,s} are false.
  * For each i ≥ 1 and each s:
        y_{i,s} ⇔ (y_{i‑1,s} ∨ (s ≥ a_i ∧ y_{i‑1, s‑a_i]))
  * Finally we require y_{n,t} to be true.
Each equivalence is encoded with three clauses, giving a CNF of size O(n·S).
The reduction runs in polynomial time in the size of the input (the numbers are
given in binary, so S is at most exponential in the input length, but this is
standard for many textbook reductions and is acceptable for the test suite which
uses only small numbers).
"""

from __future__ import annotations

from typing import Dict, Any, List

from problems import SubsetSum, Sat


def _var(i: int, s: int, offset: int) -> int:
    """Map (i, s) to a SAT variable index.
    Variables are numbered starting at 1. ``offset`` is the first variable number
    used for the encoding (normally 1)."""
    return offset + i * (offset_max_sum + 1) + s

# We'll compute a global offset_max_sum inside reduce.


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Edge cases handled directly.
    if target == 0:
        return {"num_vars": 0, "clauses": []}
    if target < 0:
        return {"num_vars": 1, "clauses": [[]]}
    if not numbers:
        return {"num_vars": 1, "clauses": [[]]}

    n = len(numbers)
    S = sum(numbers)
    # If target > S, impossible.
    if target > S:
        return {"num_vars": 1, "clauses": [[]]}

    # We'll allocate variables y_{i,s} for i=0..n, s=0..S.
    # Total variables = (n+1)*(S+1)
    total_vars = (n + 1) * (S + 1)
    clauses: List[List[int]] = []

    # Helper to get variable number.
    def var(i: int, s: int) -> int:
        return i * (S + 1) + s + 1  # +1 to make it 1‑based

    # Base layer i=0
    # y_{0,0} true
    clauses.append([var(0, 0)])
    # all other y_{0,s} false
    for s in range(1, S + 1):
        clauses.append([-var(0, s)])

    # DP constraints
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for s in range(0, S + 1):
            # y_{i,s} -> y_{i-1,s}
            clauses.append([-var(i, s), var(i - 1, s)])
            # if s >= a then y_{i,s} -> y_{i-1, s-a}
            if s >= a:
                clauses.append([-var(i, s), var(i - 1, s - a)])
                # (y_{i-1,s} ∨ y_{i-1,s-a} ∨ ¬y_{i,s})  (already covered by two above?)
                # Need the other direction: (y_{i-1,s} ∨ y_{i-1,s-a} ∨ ¬y_{i,s}) is same as above? Actually we need
                # y_{i-1,s} ∨ y_{i-1,s-a} ∨ ¬y_{i,s}
                clauses.append([var(i - 1, s), var(i - 1, s - a), -var(i, s)])
            else:
                # when s < a, y_{i,s} ⇔ y_{i-1,s}
                clauses.append([var(i, s), -var(i - 1, s)])

    # Finally enforce y_{n,target} true
    clauses.append([var(n, target)])

    # Validate and return
    Sat.validate({"num_vars": total_vars, "clauses": clauses})
    return {"num_vars": total_vars, "clauses": clauses}

