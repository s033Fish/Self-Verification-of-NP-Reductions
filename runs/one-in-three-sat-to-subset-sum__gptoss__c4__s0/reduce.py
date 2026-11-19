"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined in :class:`OneInThreeSat` (see ``problems.py``).
An instance is a dictionary ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
where each clause contains three *different* positive variable indices.

The target problem is :class:`SubsetSum`.  An instance is a dictionary
``{"numbers": [a1, a2, ...], "target": t}``.

We use the classic base‑4 encoding reduction:

* Number the clauses ``0 .. C-1``.
* For clause ``i`` define ``weight_i = 4**i``.
* For each variable ``v`` (1‑based) we create a single number equal to the sum
  of ``weight_i`` over all clauses that contain ``v``.
* The target is the sum of ``weight_i`` for *all* clauses, i.e. ``sum_{i=0}^{C-1} 4**i``.

Selecting a subset of the numbers corresponds to setting the associated
variables to ``True``.  In the base‑4 representation the digit for clause ``i``
counts how many selected variables appear in that clause.  The target has a
digit ``1`` in every position, therefore a subset reaches the target iff each
clause contributes exactly one true variable – precisely the 1‑in‑3 condition.

The reduction runs in time polynomial in the size of the input (linear in
``num_vars + number_of_clauses``) and produces non‑negative integers as
required by ``SubsetSum``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a ``OneInThreeSat`` instance to a ``SubsetSum`` instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``OneInThreeSat`` format.

    Returns
    -------
    dict
        A ``SubsetSum`` instance such that the answer is *yes* for the target
        iff the answer is *yes* for the source.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    OneInThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses → target 0, empty numbers list (any list works).
    if not clauses:
        return {"numbers": [], "target": 0}

    # Pre‑compute the base‑4 weight for each clause index.
    clause_weights: List[int] = [4 ** i for i in range(len(clauses))]

    # Build a list of numbers, one per variable (1‑based indexing).
    # Initialise with 0 and add the weight of each clause where the variable appears.
    numbers: List[int] = [0] * num_vars  # index 0 corresponds to variable 1
    for idx, clause in enumerate(clauses):
        w = clause_weights[idx]
        for var in clause:
            # ``var`` is 1‑based; convert to 0‑based list index.
            numbers[var - 1] += w

    # The target is the sum of all clause weights (i.e., a digit 1 in each base‑4 place).
    target: int = sum(clause_weights)

    # Validate the produced target instance before returning.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

