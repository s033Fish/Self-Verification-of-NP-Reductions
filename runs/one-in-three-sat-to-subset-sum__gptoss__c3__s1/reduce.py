"""Reduction from 1-in-3 SAT (positive literals) to Subset Sum.

The source problem is defined by :class:`problems.OneInThreeSat` and expects
instances of the form `{"num_vars": m, "clauses": [[a, b, c], ...]}` where
variables are numbered from `1` to `m` and each clause contains exactly
three *different* positive variables.

The target problem is :class:`problems.SubsetSum` with instances
`{"numbers": [...], "target": t}`.

Reduction strategy
-------------------
We use a classic base‑encoding reduction.  Let `C` be the number of clauses.
Choose a base `B = 4` – larger than the maximum number of true literals that
can appear in any clause (three).  For each variable `i` we construct a number
`n_i` whose base‑`B` representation has a digit `1` in position `j` iff
variable `i` occurs in clause `j` (clauses are indexed from `0`).  Formally

    n_i = sum_{j : i in clause_j} B**j

The target number is the sum of a single `1` in every clause position:

    T = sum_{j=0}^{C-1} B**j

Selecting a subset of the `n_i` corresponds exactly to choosing the variables
that are set to *true*.  In the base‑`B` representation the digit in position
`j` becomes the number of true variables in clause `j`.  Because `B` is
greater than 3, there is no carry between positions, so the sum equals `T`
iff each clause has **exactly one** true variable – precisely the requirement
of 1‑in‑3 SAT.

The reduction runs in polynomial time: we scan all clauses once to build the
numbers and compute the target.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes for validation (they raise InvalidInstance on bad input).
from problems import OneInThreeSat, SubsetSum  # noqa: F401


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 1‑in‑3 SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``OneInThreeSat`` format.

    Returns
    -------
    dict
        An instance of ``SubsetSum`` (``{"numbers": [...], "target": t}``).
    """
    # Validate the source instance; will raise InvalidInstance if malformed.
    OneInThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_vars: int = instance["num_vars"]

    BASE = 4  # larger than max true literals per clause (3)
    num_clauses = len(clauses)

    # Map each variable to the list of clause indices it appears in.
    var_to_clauses: Dict[int, List[int]] = {i: [] for i in range(1, num_vars + 1)}
    for idx, clause in enumerate(clauses):
        for var in clause:
            var_to_clauses[var].append(idx)

    numbers: List[int] = []
    for var in range(1, num_vars + 1):
        power_sum = 0
        for c_idx in var_to_clauses[var]:
            power_sum += BASE ** c_idx
        if power_sum:
            numbers.append(power_sum)
        # Variables not appearing in any clause contribute 0 and are omitted.

    target = sum(BASE ** i for i in range(num_clauses))

    result = {"numbers": numbers, "target": target}
    # Validate the produced SubsetSum instance.
    SubsetSum.validate(result)
    return result

