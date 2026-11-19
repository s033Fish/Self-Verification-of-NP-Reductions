"""Reduction from SAT to 3-SAT.

The source problem is :class:`Sat` (generic CNF).  The target problem is
``ThreeSat`` which requires every clause to contain exactly three literals on
three *different* variables.

The reduction follows the classic textbook construction:

* Remove duplicate literals and delete trivially satisfied clauses (those that
  contain a variable and its negation).
* A clause of length ``k`` is transformed as follows:
    - ``k == 0`` (the empty clause) is unsatisfiable.  We encode a contradiction
      by creating a fresh variable ``x`` together with two unit‑clause gadgets
      forcing ``x`` and ``¬x`` to be true.
    - ``k == 1`` (a unit clause) is encoded with four 3‑clauses using two fresh
      auxiliary variables ``a`` and ``b``:
        ``[ℓ, a,  b]``
        ``[ℓ, a, -b]``
        ``[ℓ, -a,  b]``
        ``[ℓ, -a, -b]``
      This gadget forces the literal ``ℓ`` to be true while respecting the
      3‑SAT format.
    - ``k == 2`` is encoded by introducing a fresh auxiliary variable ``y`` and
      adding the two clauses ``[ℓ₁, ℓ₂,  y]`` and ``[ℓ₁, ℓ₂, -y]``.
    - ``k >= 3`` is broken into a chain of 3‑clauses using fresh auxiliaries
      ``y₁ … y_{k-3}`` as described in standard reductions.

The construction runs in time linear in the size of the input formula and
produces a formula that is satisfiable iff the original one is.
"""

from __future__ import annotations

from typing import List

from problems import Sat, ThreeSat


def _encode_unit(lit: int, var_counter: List[int]) -> List[List[int]]:
    """Return a 3‑SAT gadget that forces ``lit`` to be true.

    ``var_counter`` is a one‑element list containing the current maximum variable
    index.  The function increments it by two and uses the new variables as
    auxiliaries.
    """
    a = var_counter[0] + 1
    b = var_counter[0] + 2
    var_counter[0] += 2
    return [
        [lit, a, b],
        [lit, a, -b],
        [lit, -a, b],
        [lit, -a, -b],
    ]


def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance conforms to the format required by ``ThreeSat``.
    """
    Sat.validate(instance)
    m = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]
    new_clauses: List[List[int]] = []
    var_counter = [m]  # mutable counter for fresh variables

    for clause in original_clauses:
        lit_set = set(clause)
        # Clause always true if it contains a literal and its negation.
        if any(lit in lit_set and -lit in lit_set for lit in lit_set):
            continue
        lits = list(lit_set)
        k = len(lits)
        if k == 0:
            # Unsatisfiable clause – encode x ∧ ¬x.
            x = var_counter[0] + 1
            var_counter[0] += 1
            new_clauses.extend(_encode_unit(x, var_counter))
            new_clauses.extend(_encode_unit(-x, var_counter))
        elif k == 1:
            new_clauses.extend(_encode_unit(lits[0], var_counter))
        elif k == 2:
            y = var_counter[0] + 1
            var_counter[0] += 1
            l1, l2 = lits
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        else:
            # k >= 3
            if k == 3:
                # Already a valid 3‑clause.
                new_clauses.append(lits)
            else:
                # Chain construction for longer clauses.
                y = var_counter[0] + 1
                var_counter[0] += 1
                new_clauses.append([lits[0], lits[1], y])
                idx = 2
                prev_y = y
                while idx < k - 2:
                    y = var_counter[0] + 1
                    var_counter[0] += 1
                    new_clauses.append([-prev_y, lits[idx], y])
                    prev_y = y
                    idx += 1
                # Final clause.
                new_clauses.append([-prev_y, lits[idx], lits[idx + 1]])

    result = {"num_vars": var_counter[0], "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

