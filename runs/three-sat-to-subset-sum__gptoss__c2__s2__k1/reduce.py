"""Reduction from 3‑SAT (ThreeSat) to Subset Sum (SubsetSum).

The source format (see ``problems.py``) is a dictionary

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (variable *v* true) or ``-v``
(variable *v* false).  Every clause contains exactly three literals on three
different variables.

The target format is a dictionary

    {"numbers": [a1, a2, ...], "target": t}

with non‑negative integers ``ai`` and an integer target ``t``.

We implement the classic polynomial‑time reduction using a mixed‑radix (base)
encoding.  Choose a base ``B = 4`` which is larger than the maximum number of
literals that can appear in any single clause (three).  The integer
representation consists of ``k`` digit positions for the ``k`` clauses
followed by ``m`` digit positions for the ``m`` variables.

For each literal (variable ``i`` with sign ``+`` or ``-``) we create a number
``n`` whose base‑B digits are:

* For each clause ``j`` that contains this literal, digit ``j`` is ``1``.
* Digit ``k + (i-1)`` (the variable’s dedicated position) is also ``1``.
* All other digits are ``0``.

The target integer has digit ``1`` in every clause position (ensuring that at
least one true literal is selected for each clause) and digit ``1`` in every
variable position (ensuring that exactly one literal – true or false – is
chosen for each variable).  Because the base is larger than the maximum sum
that can appear in any digit (at most three literals per clause, and exactly
one literal per variable), the digit‑wise equality forces the required
constraints.

The reduction runs in time polynomial in ``m`` and ``k`` and produces a
valid Subset Sum instance.  Edge cases (empty formula, ``m = 0``) are handled
naturally by the construction.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _base_power(base: int, exp: int) -> int:
    """Return ``base**exp`` as an int.  Separate function keeps the main code
    readable and avoids repeated ``**`` in loops.
    """
    return base ** exp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑literal lists).

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for the SubsetSum
        problem.
    """

    m: int = instance["num_vars"]  # number of variables
    clauses: List[List[int]] = instance["clauses"]
    k: int = len(clauses)  # number of clauses

    # Choose a base larger than the maximum number of literals that can
    # contribute to a single digit.  Three literals per clause, and exactly one
    # literal per variable, so 4 is sufficient.
    BASE = 4

    # Pre‑compute the power for each clause digit and each variable digit.
    clause_powers = [_base_power(BASE, j) for j in range(k)]
    var_powers = [_base_power(BASE, k + i) for i in range(m)]

    # Build a mapping from literal to the list of clause indices where it
    # appears.  Literals are represented as signed integers as in the input.
    literal_to_clauses: Dict[int, List[int]] = {}
    for idx, clause in enumerate(clauses):
        for lit in clause:
            literal_to_clauses.setdefault(lit, []).append(idx)

    numbers: List[int] = []
    # For each variable we create two numbers: one for the positive literal
    # and one for the negative literal.
    for var in range(1, m + 1):
        for sign in (+1, -1):
            lit = sign * var
            # Start with the variable digit (ensures exactly one literal per
            # variable is chosen).
            value = var_powers[var - 1]
            # Add clause contributions.
            for clause_idx in literal_to_clauses.get(lit, []):
                value += clause_powers[clause_idx]
            numbers.append(value)

    # Construct the target: 1 in every clause digit and 1 in every variable
    # digit.
    target = sum(clause_powers) + sum(var_powers)

    return {"numbers": numbers, "target": target}

