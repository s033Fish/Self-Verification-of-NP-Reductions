"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined by :class:`problems.OneInThreeSat` and the
target by :class:`problems.SubsetSum`.

Given an instance with ``m`` variables and ``C`` clauses, we construct a
base‑4 representation where each clause corresponds to a digit position.
For a variable ``i`` we create a number whose ``j``‑th digit (in base 4) is
``1`` iff variable ``i`` appears in clause ``j``.  Because each clause has at
most three variables, the sum of selected numbers never exceeds ``3`` in any
digit, so using base 4 guarantees that carries cannot occur between digit
positions.

The target is the number whose base‑4 representation consists of a single ``1``
in every digit position – i.e. ``4**0 + 4**1 + ... + 4**(C‑1)``.  Selecting a
subset of the constructed numbers corresponds exactly to choosing a truth
assignment: a clause digit sums to ``1`` iff exactly one of its three variables
is selected (set to true).  Hence the Subset‑Sum instance is a yes‑instance
iff the original 1‑in‑3‑SAT instance is satisfiable.

The reduction runs in time polynomial in the size of the input (the number of
variables and clauses) and produces integers whose bit‑length is O(C), which
is also polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import OneInThreeSat, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 1‑in‑3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`OneInThreeSat` – it
        contains the keys "num_vars" (the number of variables ``m``) and
        "clauses" (a list of length‑3 lists of variable indices).

    Returns
    -------
    dict
        A Subset‑Sum instance with keys "numbers" and "target".
    """
    # Validate the source instance – this raises InvalidInstance if malformed.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    C: int = len(clauses)

    # Base larger than the maximum possible sum per digit (3) to avoid carries.
    BASE = 4

    # Pre‑compute powers of BASE to avoid repeated exponentiation.
    base_powers: List[int] = [BASE ** j for j in range(C)]

    numbers: List[int] = []
    for var in range(1, m + 1):
        # Sum the appropriate base‑powers for each clause containing the variable.
        value = 0
        for idx, clause in enumerate(clauses):
            if var in clause:
                value += base_powers[idx]
        numbers.append(value)

    # Target has a digit 1 in every clause position.
    target = sum(base_powers)

    # The SubsetSum problem expects non‑negative integers; all our numbers are
    # non‑negative by construction.
    return {"numbers": numbers, "target": target}

