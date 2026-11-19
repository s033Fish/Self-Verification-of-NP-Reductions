"""Reduction from 3-SAT to Subset Sum.

The source problem is :class:`problems.ThreeSat` and the target is
``problems.SubsetSum``.  Both classes are defined in ``problems.py`` and expose
the usual ``validate``/``is_yes`` interface.

We use the classic polynomial‑time many‑one reduction based on a large base
representation (see e.g. Garey & Johnson, *Computers and Intractability*).

Encoding details
-----------------
* Let ``m`` be the number of variables and ``k`` the number of clauses.
* Choose a base ``B = 3``.  With this base the sum of any two digits (0/1) is
  at most ``2 < B``; therefore carries never occur when we add the encoded
  numbers.
* For each variable ``i`` (1‑based) we create two numbers:
    - ``true_i``  – selects the assignment *x_i = True*
    - ``false_i`` – selects the assignment *x_i = False*
  Both numbers have a digit ``1`` in the *variable position* ``i-1``.  In
  addition this forces the target to contain exactly one ``1`` in each variable
  position, i.e. exactly one of the two numbers must be chosen.
* Additionally, for every clause ``j`` (0‑based) we have a *clause position*
  ``m + j``.  ``true_i`` gets a ``1`` in this position iff the literal ``+i``
  appears in clause ``j``; ``false_i`` gets a ``1`` iff ``-i`` appears.
* The target vector has a ``1`` in every variable position (forcing a choice
  per variable) and a ``1`` in every clause position (forcing each clause to
  be satisfied by at least one chosen literal).

Because the maximum digit sum in any position is ``2`` (< ``B``) the integer
addition of the selected numbers exactly mirrors digit‑wise addition, and the
subset‑sum instance is solvable iff the original formula is satisfiable.

The reduction runs in time polynomial in ``m`` and ``k`` and produces numbers
that are at most ``B^{m+k}``, well within Python's arbitrary‑precision integer
capabilities.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems  # The provided module containing ThreeSat and SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` such that
        the Subset‑Sum answer is *yes* exactly when the 3‑SAT answer is *yes*.
    """
    # Validate using the source class – this also guarantees the structure.
    problems.ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k: int = len(clauses)

    B = 3  # base larger than the maximum digit sum (2)

    # Pre‑compute powers of B for all positions to avoid repeated exponentiation.
    # positions 0..m-1 are variable positions, m..m+k-1 are clause positions.
    powers: List[int] = [B ** p for p in range(m + k)]

    numbers: List[int] = []

    # Build numbers for each variable.
    for var in range(1, m + 1):
        # Digits start at 0, so variable position is var-1.
        true_num = powers[var - 1]
        false_num = powers[var - 1]
        for idx, clause in enumerate(clauses):
            if var in clause:
                # literal +var appears => true assignment satisfies clause
                true_num += powers[m + idx]
            if -var in clause:
                false_num += powers[m + idx]
        numbers.append(true_num)
        numbers.append(false_num)

    # Target: 1 in every variable position and every clause position.
    target = sum(powers)

    # Return the SubsetSum instance.
    return {"numbers": numbers, "target": target}

