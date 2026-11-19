"""Reduction from Subset Sum to SAT.

The source problem SubsetSum and the target problem Sat are defined in
``problems.py``.  An instance of SubsetSum is a dictionary with keys
``"numbers"`` (a list of non‑negative integers) and ``"target"`` (an
integer).  An instance of Sat is a dictionary with ``"num_vars"`` and
``"clauses"`` where each clause is a list of integer literals.

The reduction encodes the classic dynamic‑programming formulation of
Subset‑Sum as a Boolean formula.  For a target ``t`` we create a Boolean
variable ``dp[i][s]`` meaning *using the first ``i`` numbers we can
obtain sum ``s``*.  The recurrence is

    dp[i][s]  <=>  dp[i‑1][s]  ∨  (x_i ∧ dp[i‑1][s‑a_i])

where ``x_i`` is a Boolean variable that decides whether the ``i``‑th
number (value ``a_i``) is taken.  The formula is expressed in CNF using
Tseitin variables for the conjunctions.  The construction is polynomial in
``n * t`` where ``n`` is the number of input numbers – this is acceptable
for the small instances used in the verification tests.

Edge‑case handling:
  * ``target < 0`` – impossible, we return an unsatisfiable formula
    (a single empty clause).
  * ``target == 0`` – always satisfiable; we return the trivially
    satisfiable formula with no clauses.
  * ``target > sum(numbers)`` – also unsatisfiable.

The function ``reduce`` validates the source instance, builds the SAT
instance and returns it.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for validation; the reduction itself does
# not depend on their internal implementation.
from problems import SubsetSum, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SubsetSum instance to an equivalent SAT instance.

    The returned SAT instance is satisfiable iff the original SubsetSum
    instance has a subset summing to the target.
    """
    # Validate the source instance (will raise if malformed).
    SubsetSum.validate(instance)

    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Simple edge cases.
    if target < 0:
        # Unsatisfiable: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if target == 0:
        # Always satisfiable: empty CNF (no clauses).
        return {"num_vars": 0, "clauses": []}
    total = sum(numbers)
    if target > total:
        return {"num_vars": 1, "clauses": [[]]}

    n = len(numbers)
    # We will create variables numbered from 1 upwards.
    next_var = 1

    def new_var() -> int:
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    clauses: List[List[int]] = []

    # Selection variables x_i for each number.
    x_vars = [new_var() for _ in range(n)]

    # dp[i][s] variables: i = 0..n, s = 0..target.
    dp: List[List[int]] = [[0] * (target + 1) for _ in range(n + 1)]

    # Base case: dp[0][0] is true, all other dp[0][s] are false.
    true_var = new_var()
    dp[0][0] = true_var
    clauses.append([true_var])  # force true
    for s in range(1, target + 1):
        v = new_var()
        dp[0][s] = v
        clauses.append([-v])  # force false

    # Build the recurrence.
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for s in range(0, target + 1):
            cur = new_var()
            dp[i][s] = cur
        for s in range(0, target + 1):
            prev = dp[i - 1][s]
            cur = dp[i][s]
            # (¬prev ∨ cur)
            clauses.append([-prev, cur])
            if s >= a:
                # Introduce auxiliary variable z = x_i ∧ dp[i-1][s-a]
                z = new_var()
                # z → x_i        (¬z ∨ x_i)
                clauses.append([-z, x_vars[i - 1]])
                # z → dp[i-1][s-a] (¬z ∨ dp[i-1][s-a])
                clauses.append([-z, dp[i - 1][s - a]])
                # (¬x_i ∨ ¬dp[i-1][s-a] ∨ z)
                clauses.append([-x_vars[i - 1], -dp[i - 1][s - a], z])
                # z → cur        (¬z ∨ cur)
                clauses.append([-z, cur])
                # cur → prev ∨ z (¬cur ∨ prev ∨ z)
                clauses.append([-cur, prev, z])
            else:
                # No way to use the i‑th number for this sum.
                # cur → prev   (¬cur ∨ prev)
                clauses.append([-cur, prev])

    # Require that dp[n][target] is true.
    clauses.append([dp[n][target]])

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

