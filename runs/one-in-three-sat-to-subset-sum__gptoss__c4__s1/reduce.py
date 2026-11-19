"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is :class:`OneInThreeSat` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

We implement a classic base‑encoding reduction.  For each clause we reserve a
digit position in a mixed‑radix representation with base ``B = 4``.  The base is
chosen larger than the maximum number of literals that can contribute to a
clause (which is 3) so that carries never occur when we add the numbers
corresponding to the variables set to *true*.

For a variable ``v`` we create a number ``N_v`` whose ``i``‑th digit (weight
``B**i``) is ``1`` iff ``v`` appears in clause ``i`` and ``0`` otherwise.  A
subset of these numbers corresponds exactly to the set of variables assigned
true.  The sum of the selected numbers therefore has digit ``i`` equal to the
number of true literals in clause ``i``.  The formula is satisfied iff each
clause has **exactly one** true literal, i.e. each digit equals ``1``.

The target sum is therefore ``T = 1 + B + B**2 + ... + B**(c-1)`` where ``c``
is the number of clauses.  Because ``B`` is larger than the maximum possible
digit sum (3), the equality of the integer sums is equivalent to the digit‑wise
condition.

Edge cases:
* No clauses – the target is ``0`` and the empty subset always achieves it.
* Variables that never appear in any clause receive the number ``0``; they may
  be arbitrarily chosen in the subset without affecting the sum, which does
  not change correctness.

The reduction runs in time polynomial in the size of the input (O(m·c) to
compute the numbers and O(c) to compute the target).
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3 SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary representing a ``OneInThreeSat`` instance.  It must have
        the keys ``"num_vars"`` and ``"clauses"`` as described in the problem
        docstring.

    Returns
    -------
    dict
        A dictionary representing a ``SubsetSum`` instance with keys
        ``"numbers"`` and ``"target"``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Base larger than the maximum clause size (3).  4 is the smallest such
    # integer and keeps numbers reasonably small.
    B = 4

    # Pre‑compute powers of B to avoid recomputation.
    powers = [B ** i for i in range(c)]

    # For each variable compute its contribution.
    numbers: List[int] = []
    for v in range(1, m + 1):
        val = 0
        for idx, clause in enumerate(clauses):
            if v in clause:
                val += powers[idx]
        numbers.append(val)

    # Target sum: one in each digit position.
    target = sum(powers)

    # Validate the target instance before returning (helps catch bugs).
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

