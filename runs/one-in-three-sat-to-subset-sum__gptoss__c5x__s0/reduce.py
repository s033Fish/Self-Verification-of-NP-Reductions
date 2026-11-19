"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined in ``problems.OneInThreeSat`` and expects an
instance of the form ``{"num_vars": m, "clauses": [[a, b, c], ...]}`` where
each clause contains three *different* positive variable indices.

We construct a classic base‑encoding reduction:

* Choose a base ``B = 4``.  The base is larger than the maximum possible
  contribution per clause (at most three true variables) so that no carry
  can occur when adding the encoded numbers.
* For each clause ``c`` (enumerated from ``0``) we reserve the digit
  ``B**c``.
* For each variable ``x_i`` we create a number that has a ``1`` in the digit
  positions of the clauses in which ``x_i`` appears.  Concretely

    ``num_i = sum_{c where i in clause_c} B**c``

* The target number is the sum of a single ``1`` in each clause position:

    ``target = sum_{c=0}^{C-1} B**c`` where ``C`` is the number of clauses.

Selecting a subset of the variable numbers corresponds to setting exactly
those variables to ``True``.  Because carries are impossible, the digit for a
clause equals the number of true variables in that clause.  The target forces
each digit to be exactly ``1`` – i.e. exactly one true variable per clause.

Edge cases:
  * If there are no clauses the target is ``0`` and we can return an empty
    number list – the empty subset trivially sums to ``0``.
  * Variables that never appear in any clause would contribute ``0``; they are
    omitted because they do not affect the sum.

The reduction runs in time polynomial in the size of the input (O(m + C)).
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat as SOURCE  # noqa: F401 – kept for clarity
from problems import SubsetSum as TARGET  # noqa: F401 – kept for clarity


def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``OneInThreeSat`` format.

    Returns
    -------
    dict
        An instance of ``SubsetSum`` (``{"numbers": [...], "target": t}``).
    """
    # Validate the source instance – will raise InvalidInstance on bad input.
    SOURCE.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # No clauses → target 0, empty numbers list (any assignment works).
    if not clauses:
        return {"numbers": [], "target": 0}

    base = 4  # Must be > max literals per clause (3) to avoid carries.
    num_clauses = len(clauses)

    # Pre‑compute powers of the base for each clause index.
    powers = [base ** i for i in range(num_clauses)]

    # Build a mapping from variable to the sum of its clause‑powers.
    var_sums = [0] * (num_vars + 1)  # 1‑based indexing; index 0 unused.
    for idx, clause in enumerate(clauses):
        weight = powers[idx]
        for var in clause:
            var_sums[var] += weight

    # Omit variables that never appear (their sum would be 0).
    numbers = [value for value in var_sums[1:] if value != 0]

    # Target: one unit in each clause position.
    target = sum(powers)

    # Validate the produced target instance.
    result = {"numbers": numbers, "target": target}
    TARGET.validate(result)
    return result

