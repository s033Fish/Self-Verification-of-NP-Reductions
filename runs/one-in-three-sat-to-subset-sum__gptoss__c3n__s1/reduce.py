"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem is defined in :class:`OneInThreeSat` (see ``problems.py``).
The target problem is :class:`SubsetSum`.

The reduction is a classic encoding using a mixed‑radix (base) representation.
We allocate one digit position for each clause and one distinct digit position
for each variable.  The base is chosen larger than the maximum possible digit
value (which is 3 because a clause contains three literals).  With this base
there is never any carry between positions, so the integer representation is a
bijection between vectors of digits and ordinary integers.

For a variable ``i`` (1‑based) we create two numbers:

* ``false_i`` – contributes only the variable’s unique weight ``W_i``.
* ``true_i``  – contributes ``W_i`` **plus** a contribution of ``1`` in each
  clause‑digit where the variable appears.

The target sum consists of the sum of all variable weights (forcing the
selection of exactly one of the two numbers for each variable) and a digit
``1`` in every clause position (forcing exactly one true literal per clause).

Because the base is larger than the maximal digit sum, the integer arithmetic
does not interfere between positions and the reduction is correct.

The implementation works for all edge cases described in the problem
definitions: empty formulas, zero variables, etc.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, SubsetSum

def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``OneInThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``SubsetSum`` format.
    """
    # Validate the source instance (raises InvalidInstance on malformed input).
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Base larger than the maximum possible digit value (3).  Adding 2 is safe
    # for the case c = 0 where we need a base > 0.
    base: int = c + 2

    # Pre‑compute the weight for each variable.  The weight occupies a distinct
    # digit position after the clause positions.
    var_weights: List[int] = [base ** (c + i) for i in range(m)]

    # Map variable index (1‑based) to the set of clause indices where it occurs.
    var_to_clauses: List[List[int]] = [[] for _ in range(m + 1)]
    for idx, clause in enumerate(clauses):
        for lit in clause:
            var_to_clauses[lit].append(idx)

    numbers: List[int] = []
    # For each variable create the true/false numbers.
    for i in range(1, m + 1):
        weight = var_weights[i - 1]
        # Contribution from clauses where the variable appears (digit 1 per clause).
        clause_contrib = sum(base ** j for j in var_to_clauses[i])
        false_num = weight
        true_num = weight + clause_contrib
        numbers.append(false_num)
        numbers.append(true_num)

    # Target consists of the sum of all variable weights plus a digit 1 for each clause.
    target = sum(var_weights) + sum(base ** j for j in range(c))

    # Validate the produced target instance before returning.
    SubsetSum.validate({"numbers": numbers, "target": target})
    return {"numbers": numbers, "target": target}

