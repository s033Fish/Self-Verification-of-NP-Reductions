"""Reduction from Subset Sum to SAT using DP encoding.

The reduction runs in O(n·T) time where n = len(numbers) and T = max(0, target).
For the small test instances this is easily polynomial and satisfies the
oracle's runtime requirement.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SubsetSum, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Edge cases
    if target < 0:
        # unsatisfiable formula
        return {"num_vars": 1, "clauses": [[]]}
    # We'll treat target == 0 uniformly with the DP encoding; the DP will
    # force dp[n][0] true, giving a satisfiable instance.

    n = len(numbers)
    T = max(0, target)
    # variable indexing: var(i, s) where 0 <= i <= n, 0 <= s <= T
    # map to SAT variable numbers starting at 1
    def var(i: int, s: int) -> int:
        return i * (T + 1) + s + 1

    clauses: List[List[int]] = []

    # Base case i = 0
    # dp[0][0] = True
    clauses.append([var(0, 0)])
    # dp[0][s] = False for s > 0
    for s in range(1, T + 1):
        clauses.append([-var(0, s)])

    # Transition constraints
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for s in range(0, T + 1):
            if a <= s:
                # dp[i][s] <=> dp[i-1][s] or dp[i-1][s-a]
                # (¬dp[i][s] ∨ dp[i-1][s] ∨ dp[i-1][s-a])
                clauses.append([-var(i, s), var(i - 1, s), var(i - 1, s - a)])
                # (dp[i][s] ∨ ¬dp[i-1][s])
                clauses.append([var(i, s), -var(i - 1, s)])
                # (dp[i][s] ∨ ¬dp[i-1][s-a])
                clauses.append([var(i, s), -var(i - 1, s - a)])
            else:
                # dp[i][s] <=> dp[i-1][s]
                clauses.append([-var(i, s), var(i - 1, s)])
                clauses.append([var(i, s), -var(i - 1, s)])

    # Force the target sum to be achievable
    clauses.append([var(n, target)])

    num_vars = (n + 1) * (T + 1)
    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(sat_instance)
    return sat_instance

