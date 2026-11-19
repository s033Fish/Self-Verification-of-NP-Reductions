"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem instance format (as defined in ``problems.py``) is::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *distinct* positive variable indices.
The target problem (Subset Sum) expects a dictionary of the form::

    {"numbers": [a1, a2, ...], "target": t}

We construct a classic base‑encoding reduction.  Choose a base ``B`` larger
than the maximum possible sum in any digit position – because each clause
contains at most three variables, ``B = 4`` suffices.  For each variable ``v``
we create a number whose ``i``‑th digit (in base ``B``) is ``1`` iff ``v``
appears in clause ``i``.  The target number has digit ``1`` in every clause
position.  Selecting a subset of the variable numbers that sums to the target
exactly corresponds to picking a set of variables that makes *exactly one*
variable true in each clause.

The construction runs in polynomial time and the integers involved have at
most ``O(#clauses)`` bits, so the reduction satisfies the required complexity
constraints.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3 SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of variable indices).

    Returns
    -------
    dict
        A Subset Sum instance ``{"numbers": [...], "target": t}`` such that
        the Subset Sum instance is a *yes* instance iff the original SAT
        instance is satisfiable with exactly one true literal per clause.
    """

    num_vars: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Base larger than the maximum number of true literals that can appear in
    # a single clause (which is 3 for 1‑in‑3 SAT).  Using 4 guarantees that no
    # carries occur when we sum the numbers.
    BASE = 4

    # Pre‑compute the contribution of each clause position as BASE**i.
    # This is safe because Python integers have arbitrary precision.
    clause_weights = [BASE ** i for i in range(len(clauses))]

    # Build a number for each variable.
    numbers: List[int] = []
    for var in range(1, num_vars + 1):
        total = 0
        for weight, clause in zip(clause_weights, clauses):
            # Clause lists are guaranteed to contain distinct variables.
            if var in clause:
                total += weight
        numbers.append(total)

    # The target has a digit 1 in every clause position, i.e. sum of all
    # clause_weights.
    target = sum(clause_weights)

    return {"numbers": numbers, "target": target}

