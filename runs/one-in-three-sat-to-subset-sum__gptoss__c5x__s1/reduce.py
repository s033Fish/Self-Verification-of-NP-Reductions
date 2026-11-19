"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined in :class:`OneInThreeSat` in ``problems.py``.
An instance is a dictionary ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
where each clause contains three *different* positive variable indices.

The target problem is :class:`SubsetSum`.  An instance is a dictionary
``{"numbers": [a1, a2, ...], "target": t}`` where the numbers are
non‑negative integers.

**Idea of the reduction**
--------------------------
We treat each clause as a digit position in a mixed‑radix representation.
Choose a base ``B`` larger than the maximum possible digit sum.  In a
1‑in‑3‑SAT clause at most three variables can contribute to the digit, and we
need the sum to be exactly ``1``.  Therefore ``B = 4`` is sufficient – the
digit values ``0,1,2,3`` never cause a carry when summed.

For each variable ``x_i`` we create a number whose base‑``B`` representation
has a ``1`` in every clause where ``x_i`` appears and ``0`` elsewhere.  The
target number has a ``1`` in *every* clause digit.  Selecting a subset of the
variable numbers corresponds to setting exactly those variables to ``True``.
The digit‑wise sum of the selected numbers equals the target iff each clause
has exactly one true variable.

The construction runs in time polynomial in the size of the input (linear
in the number of variable‑clause incidences).
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum


def _encode_number(variable: int, clause_indices: List[int], base: int) -> int:
    """Return the integer encoding for a variable.

    ``clause_indices`` is the list of clause positions (0‑based) in which the
    variable appears.  The encoding is ``sum(base**c for c in clause_indices)``.
    """
    value = 0
    for c in clause_indices:
        value += base ** c
    return value


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to a SubsetSum instance.

    The returned dictionary follows the format required by ``SubsetSum``:
    ``{"numbers": [...], "target": t}``.
    """
    # Validate the source instance using the provided validator.
    OneInThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses – the target is 0 and any (including empty) set of
    # numbers works.  Returning an empty list is sufficient.
    if not clauses:
        return {"numbers": [], "target": 0}

    # Choose a base larger than the maximum possible digit sum (3).
    BASE = 4

    # Map each variable to the list of clause indices where it appears.
    var_to_clauses: Dict[int, List[int]] = {i: [] for i in range(1, num_vars + 1)}
    for idx, clause in enumerate(clauses):
        for var in clause:
            var_to_clauses[var].append(idx)

    numbers: List[int] = []
    for var in range(1, num_vars + 1):
        # If a variable does not appear in any clause its contribution is 0;
        # such a number is unnecessary for the reduction, so we skip it.
        clauses_of_var = var_to_clauses[var]
        if clauses_of_var:
            numbers.append(_encode_number(var, clauses_of_var, BASE))

    # Target has digit 1 in every clause position.
    target = sum(BASE ** i for i in range(len(clauses)))

    # Validate the target instance before returning.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

