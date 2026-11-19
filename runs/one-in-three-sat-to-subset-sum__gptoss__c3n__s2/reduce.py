"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined in :class:`OneInThreeSat` (see ``problems.py``).
An instance is a dictionary ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
where each clause contains three *distinct* positive variable indices.

The target problem is :class:`SubsetSum`.  An instance is a dictionary
``{"numbers": [a1, a2, ...], "target": t}`` where the numbers are
non‑negative integers.

**Reduction idea**
-------------------
We encode each clause as a digit in a large base ``B``.  Choose ``B = 4``.
For clause ``i`` (0‑based) we will use the weight ``B**i``.  For variable ``v``
we create a number that has a ``1`` in the digit of each clause that contains
``v`` and ``0`` elsewhere.  Formally::

    number(v) = sum_{i | v in clause i} B**i

If we select a subset of these numbers (i.e. set the corresponding variables
to *true*), the digit in position ``i`` of the total sum equals the number of
true literals in clause ``i``.  Because each clause contains at most three
variables, the digit never exceeds ``3``.  By picking ``B = 4`` we guarantee
that no carries occur during addition.

The target sum therefore has digit ``1`` in every clause position:

    target = sum_{i=0}^{#clauses-1} B**i

Thus a subset reaches the target exactly when each clause contributes a sum
of ``1`` – i.e. exactly one variable in each clause is true.

The construction runs in time polynomial in the size of the input (linear in
the number of variables plus clauses) and satisfies all edge cases:

* If there are no clauses, ``target = 0`` and the numbers list may be empty.
  Subset‑Sum with target ``0`` is always a yes‑instance, matching the source.
* Variables that never appear in any clause produce the number ``0``; they can
  safely be omitted because selecting them does not affect the sum.

The function ``reduce`` performs this transformation and returns a valid
Subset‑Sum instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a positive 1‑in‑3‑SAT instance to Subset Sum.

    Parameters
    ----------
    instance:
        A dictionary representing a ``OneInThreeSat`` instance.  It is
        assumed to be validated beforehand (or the caller may rely on the
        ``validate`` method of the source class).

    Returns
    -------
    dict
        A dictionary representing a ``SubsetSum`` instance that is a
        polynomial‑time equivalent of the input.
    """
    # Validate the source instance to catch malformed inputs early.
    OneInThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Base larger than the maximum possible sum per digit (3) to avoid
    # carries.  4 is the smallest such integer.
    BASE = 4

    # Pre‑compute the weight for each clause position.
    clause_weights = [BASE ** i for i in range(len(clauses))]

    # Build a number for each variable.  Variables are numbered 1..num_vars.
    numbers: List[int] = []
    for var in range(1, num_vars + 1):
        weight = 0
        for idx, clause in enumerate(clauses):
            if var in clause:
                weight += clause_weights[idx]
        # Only include non‑zero numbers; a zero would be redundant.
        if weight:
            numbers.append(weight)

    # Target: digit 1 in each clause position.
    target = sum(clause_weights)

    reduced_instance = {"numbers": numbers, "target": target}
    # Ensure the produced instance is valid for the target problem.
    SubsetSum.validate(reduced_instance)
    return reduced_instance

