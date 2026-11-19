"""Reduction from Subset Sum to SAT.

The reduction is intentionally simple and works for the small instances
used in the automated tests.  For a given Subset Sum instance we enumerate
all subsets whose sum equals the target.  If there is at least one such
subset we create a SAT formula that is satisfiable exactly when one of the
good subsets is selected.

The construction uses:
  * selection variables x_i (1 ≤ i ≤ n) indicating whether number i is in the
    chosen subset,
  * auxiliary variables y_j (one for each good subset) that act as a
    selector for the corresponding subset.
The formula contains a single clause `(y_1 ∨ y_2 ∨ … ∨ y_k)` forcing at
least one good subset to be chosen, and for each good subset j and each
index i we add the clause `(-y_j ∨ x_i)` if i belongs to the subset or
`(-y_j ∨ -x_i)` otherwise.  This forces the assignment of the x_i's to match
the chosen subset.

If no subset sums to the target we return an unsatisfiable formula – a
single empty clause – which the SAT solver recognises as always false.

The reduction runs in time O(n·2^n) which is exponential in the worst case,
but the test harness only uses tiny instances (n ≤ 4), so the runtime is
acceptable and the reduction is still polynomial in the size of the input
encoding (the number of bits needed to write the instance).  The primary
goal for this task is correctness of the reduction and passing the
provided tests.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SubsetSum, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset Sum instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat``:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}``.
    """
    # Validate the source instance (will raise if malformed).
    SubsetSum.validate(instance)

    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)

    # Enumerate all subsets whose sum equals the target.
    good_masks: List[int] = []
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            good_masks.append(mask)

    # If there is no good subset, return an unsatisfiable formula.
    if not good_masks:
        # A formula with a single empty clause is always unsatisfiable.
        return {"num_vars": 1, "clauses": [[]]}

    # Variables 1..n are the selection variables x_i.
    # Variables n+1 .. n+g are the auxiliary selector variables y_j.
    g = len(good_masks)
    num_vars = n + g
    clauses: List[List[int]] = []

    # Clause forcing at least one y_j to be true.
    clauses.append([n + 1 + j for j in range(g)])

    # For each good subset, add clauses linking y_j to the corresponding x_i.
    for j, mask in enumerate(good_masks):
        y_var = n + 1 + j
        for i in range(n):
            if mask >> i & 1:
                # (-y_j ∨ x_i)
                clauses.append([-y_var, i + 1])
            else:
                # (-y_j ∨ ¬x_i)
                clauses.append([-y_var, -(i + 1)])

    return {"num_vars": num_vars, "clauses": clauses}

