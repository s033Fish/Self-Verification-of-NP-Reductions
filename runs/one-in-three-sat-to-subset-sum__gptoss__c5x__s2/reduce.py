"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined in :class:`OneInThreeSat` (see ``problems.py``).
An instance is a dictionary ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
where each clause contains three *different* positive variable indices.

The target problem is :class:`SubsetSum`.  An instance is a dictionary
``{"numbers": [a1, a2, ...], "target": t}``.

We implement the classic polynomial‑time reduction using a large base
representation.  Let ``m`` be the number of variables and ``k`` the number of
clauses.  Choose a base ``B = m + 1`` – this is strictly larger than the
maximum possible digit sum in any position, guaranteeing that addition of the
numbers never creates carries between clause‑positions.

For clause ``j`` (0‑based) we associate the weight ``w_j = B**j``.  For each
variable ``i`` we create a number that is the sum of the weights of the clauses
in which ``i`` appears:

    number_i = sum_{j : i in clause j} w_j

The Subset Sum target is the sum of *all* clause weights, i.e. exactly one
contribution per clause:

    target = sum_{j=0}^{k-1} w_j

Selecting a subset of the numbers corresponds to setting the associated
variables to ``True``.  Because the base is larger than ``m``, the digit for a
clause ``j`` in the total sum equals the number of selected variables that
appear in that clause.  The equality ``sum == target`` therefore forces each
clause digit to be exactly ``1`` – i.e. exactly one true variable per clause.

If there are no clauses (``k == 0``) the target is ``0`` and the numbers list is
empty; Subset Sum correctly answers *yes* for target ``0``.

The function runs in time polynomial in the size of the input (O(m·k) arithmetic
operations) and produces a valid Subset Sum instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3‑SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`OneInThreeSat`.

    Returns
    -------
    dict
        A dictionary adhering to the format of :class:`SubsetSum`.
    """
    # Validate the source instance (will raise if malformed).
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k = len(clauses)

    # Base larger than the maximum possible digit sum (which is at most m).
    B = m + 1  # B >= 1, works even for m = 0 (B = 1) – but with no clauses target is 0.

    # Pre‑compute powers B**j for each clause index.
    weights = [B ** j for j in range(k)]

    # Build numbers for each variable (1‑based indexing).
    numbers: List[int] = []
    for var in range(1, m + 1):
        total = 0
        for idx, clause in enumerate(clauses):
            if var in clause:
                total += weights[idx]
        numbers.append(total)

    # Target is the sum of all clause weights (exactly one per clause).
    target = sum(weights)

    # Validate the produced target instance.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

