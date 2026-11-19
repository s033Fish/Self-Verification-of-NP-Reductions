"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem instance is a dictionary with keys ``num_vars`` and
``clauses`` as described in ``problems.py``.  The target problem instance is a
dictionary with keys ``numbers`` (a list of non‑negative integers) and
``target`` (an integer).

Reduction idea
==============
We encode each clause as a digit in a mixed‑radix representation.  Let C be the
number of clauses.  Choose a base ``B = C + 1``.  For each variable *v* we
create a number whose ``j``‑th digit (in base ``B``) is ``1`` iff variable *v*
appears in clause ``j`` and ``0`` otherwise.  The target number has digit ``1``
in every position, i.e. it equals ``B**0 + B**1 + ... + B**(C-1)``.

Because the digits are bounded by ``B-1``, the representation of a sum of such
numbers is unique.  Selecting a subset of variable‑numbers yields a sum whose
``j``‑th digit equals the number of selected variables that appear in clause
``j``.  The sum matches the target exactly iff each clause receives exactly
one selected variable – precisely the requirement of 1‑in‑3 SAT.

Edge cases
----------
* If there are no clauses (C = 0) the target is ``0`` and the numbers list can
  be empty.  Subset‑Sum with target ``0`` is always a YES instance, matching the
  source problem definition.
* Variables that never appear in any clause simply contribute ``0`` to the
  numbers list; they can be omitted without affecting correctness.

The reduction runs in time polynomial in the size of the source instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum

def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3 SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary validated by :class:`OneInThreeSat`.  It contains the
        keys ``"num_vars"`` (int) and ``"clauses"`` (list of three‑element
        lists of variable indices).

    Returns
    -------
    dict
        A Subset‑Sum instance with keys ``"numbers"`` and ``"target"``.
    """
    # Validate the source instance – this will raise if malformed.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    C = len(clauses)

    # Base for the mixed‑radix representation.  Using C+1 guarantees that the
    # digit sum in any position never reaches the base, preserving uniqueness.
    base = C + 1

    # Pre‑compute powers of the base for each clause index.
    pow_base = [base ** i for i in range(C)]

    # Build a number for each variable.  Variables are 1‑indexed.
    numbers: List[int] = []
    for var in range(1, m + 1):
        # Sum base**j over all clauses j where `var` appears.
        value = 0
        for j, clause in enumerate(clauses):
            if var in clause:
                value += pow_base[j]
        # A variable that never appears contributes 0; we can safely omit it.
        if value:
            numbers.append(value)

    # Target number: digit 1 in every clause position.
    target = sum(pow_base)

    reduced = {"numbers": numbers, "target": target}
    # Validate the produced target instance.
    SubsetSum.validate(reduced)
    return reduced

