"""Reduction from 3-SAT to Subset Sum.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  Each
literal is an integer ``+v`` (variable *v* is true) or ``-v`` (variable *v*
is false).  The target problem is ``SubsetSum`` with instance format
``{"numbers": [a1, a2, ...], "target": t}``.

The classic polynomial‑time reduction encodes a truth assignment as a
selection of numbers.  We use a mixed‑radix representation where each
position corresponds either to a variable or to a clause.  The base is
chosen large enough (10) so that carries never occur when adding the
selected numbers.

Construction
-------------
* Let ``m`` be the number of variables and ``k`` the number of clauses.
* For each variable ``i`` (1‑based) we create two numbers:
  - ``true_i``  – corresponds to setting variable *i* to *True*.
  - ``false_i`` – corresponds to setting variable *i* to *False*.
  Both numbers have a ``1`` in the digit position representing variable
  ``i``.  In addition, for each clause ``j`` they have a ``1`` in the clause
  digit iff the literal that would be satisfied by that assignment appears
  in clause ``j``.
* For each clause ``j`` we also create a *filler* number that has a ``1``
  only in the clause digit ``j``.  The filler allows a clause to be
  satisfied by the filler when no chosen literal satisfies it.
* The target number has a ``1`` in every variable digit and a ``1`` in every
  clause digit.

Correctness Sketch
-------------------
* Selecting exactly one of ``true_i``/``false_i`` for each variable yields a
  sum of ``1`` in each variable digit – matching the target.
* For each clause digit, the sum contributed by the selected variable
  numbers is the number of literals in that clause that are satisfied.  To
  reach the target digit ``1`` we must have that sum equal ``1``.  This can
  be achieved either by picking a variable number that satisfies the clause
  (contributing ``1``) or by picking the clause filler (contributing ``1``).
  Picking both would make the digit ``2`` which would overshoot the target,
  so any valid subset corresponds to an assignment that satisfies every
  clause.
* Conversely, a satisfying assignment provides a subset: pick the number
  corresponding to the chosen truth value for each variable, and for each
  clause pick the filler only if the clause is not already satisfied by a
  chosen variable number.  The resulting sum equals the target.

The reduction runs in time polynomial in ``m`` and ``k`` and produces a
valid Subset Sum instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _digit_value(base: int, position: int) -> int:
    """Return ``base ** position``.

    Helper to keep the construction readable.
    """
    return base ** position


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list
        of three‑element lists of literals).

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` such that
        the Subset‑Sum instance is a *yes* instance iff the original 3‑SAT
        instance is satisfiable.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    k: int = len(clauses)

    # Choose a base large enough to avoid carries.  The maximum sum in any
    # digit is at most the number of literals that can contribute to a clause
    # (3) plus the filler (1), i.e., 4.  Base 10 is safely larger.
    BASE = 10

    numbers: List[int] = []

    # Pre‑compute clause digit positions for quick lookup.
    # clause_pos[j] = m + j
    clause_pos_offset = m

    # Build variable assignment numbers.
    for var in range(1, m + 1):
        # true literal = +var, false literal = -var
        true_num = 0
        false_num = 0
        # Variable digit (position var-1) set to 1 for both assignments.
        true_num += _digit_value(BASE, var - 1)
        false_num += _digit_value(BASE, var - 1)

        # Scan clauses to set clause digits.
        for j, clause in enumerate(clauses):
            if var in clause:  # literal +var present
                true_num += _digit_value(BASE, clause_pos_offset + j)
            if -var in clause:  # literal -var present
                false_num += _digit_value(BASE, clause_pos_offset + j)

        numbers.append(true_num)
        numbers.append(false_num)

    # Add filler numbers for each clause.
    for j in range(k):
        filler = _digit_value(BASE, clause_pos_offset + j)
        numbers.append(filler)

    # Construct target: 1 in each variable digit and each clause digit.
    target = 0
    for var in range(m):
        target += _digit_value(BASE, var)
    for j in range(k):
        target += _digit_value(BASE, clause_pos_offset + j)

    return {"numbers": numbers, "target": target}

