"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is :class:`OneInThreeSat` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For a formula with ``C`` clauses we use a base ``B = 4`` (greater than the
maximum possible contribution of a clause, which is 3).  For each variable
``x_i`` we create a number that has a ``1`` in the digit corresponding to each
clause that contains ``x_i`` and ``0`` elsewhere.  In base ``B`` this number is
simply the sum of ``B**j`` for every clause ``j`` that contains the variable.

The target value is the number whose representation in base ``B`` consists of
exactly one ``1`` in each clause position, i.e. ``sum_{j=0}^{C-1} B**j``.

Choosing a subset of the variable numbers corresponds to setting those
variables to ``True``.  The digit in position ``j`` of the resulting sum is the
number of true variables in clause ``j``.  Because ``B`` is larger than the
maximum possible digit (3) there are no carries, and the sum equals the target
iff each clause has exactly one true variable.

Edge cases:
* If there are no clauses, the target is ``0`` and the numbers list can be
  empty – Subset Sum is trivially satisfied (empty sub‑list) which matches the
  fact that an empty 1‑in‑3‑SAT instance is a YES instance.
* Variables that never appear generate a number ``0``; they do not affect the
  sum and may be included or omitted arbitrarily.

The ``reduce`` function validates the input using the problem class' ``validate``
method and returns a dictionary suitable for the ``SubsetSum`` problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum


def _base_power(base: int, exp: int) -> int:
    """Return ``base**exp`` using Python's built‑in pow (fast for small ints)."""
    return pow(base, exp)


def reduce(instance: Dict) -> Dict:
    """Reduce a positive 1‑in‑3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary representing a ``OneInThreeSat`` instance.

    Returns
    -------
    dict
        A dictionary representing a ``SubsetSum`` instance such that the
        Subset‑Sum instance is a YES instance iff the original SAT instance is
        a YES instance.
    """
    # Validate the source instance – will raise InvalidInstance on bad input.
    OneInThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    C = len(clauses)

    # Base larger than the maximum possible sum per clause (3).  4 is the
    # smallest convenient choice and keeps numbers reasonably sized.
    BASE = 4

    # Pre‑compute powers of BASE for each clause index to avoid repeated pow.
    base_powers = [_base_power(BASE, j) for j in range(C)]

    # Build the list of numbers, one per variable (1‑based indexing).
    numbers: List[int] = []
    for var in range(1, num_vars + 1):
        value = 0
        for clause_index, clause in enumerate(clauses):
            if var in clause:
                value += base_powers[clause_index]
        numbers.append(value)

    # Target: one ``1`` in each clause digit.
    target = sum(base_powers)  # equals (BASE**C - 1) // (BASE - 1) when C>0

    # Validate the produced target instance before returning.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

