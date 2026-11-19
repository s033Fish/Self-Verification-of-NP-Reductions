"""Reduction from 3-SAT to Subset Sum.

The reduction follows the classic textbook construction (see e.g. Garey &
Johnson).  For a 3‑SAT instance with ``m`` variables and ``n`` clauses we
create a Subset‑Sum instance with numbers represented in base ``B = 10``.

* Each number has ``n + m`` digits.  The first ``n`` digits correspond to the
  clauses, the last ``m`` digits correspond to the variables.
* For each variable ``i`` we create two numbers – one representing the
  assignment ``x_i = True`` and one for ``x_i = False``.  In the clause part
  of the number a digit is ``1`` iff the literal appears in that clause.  In
  the variable part both numbers have a ``1`` in the column of variable ``i``.
  This forces the subset to pick exactly one of the two numbers for each
  variable because the target digit for each variable column is ``1`` and the
  base ``B`` is larger than the maximum possible column sum (which is ``2``).
* For each clause we add a *clause‑filler* number that has a ``1`` only in the
  clause column.  The target digit for each clause column is ``2`` – one from
  the filler and one from a literal that satisfies the clause.  Because the
  base ``B`` is larger than the maximal column sum (``3`` literals + filler =
  ``4``) no carries occur.

The resulting Subset‑Sum instance is a “yes’’ instance iff the original 3‑SAT
instance is satisfiable.  The construction runs in time polynomial in the
size of the formula.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _digits_to_int(digits: List[int], base: int = 10) -> int:
    """Convert a list of base‑``base`` digits (most‑significant first) to an int.

    ``digits`` may contain values in ``0..base-1``.  The function simply
    interprets the list as a positional representation.
    """
    value = 0
    for d in digits:
        value = value * base + d
    return value


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to Subset Sum.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for the Subset Sum
        problem defined in ``problems.py``.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    n = len(clauses)

    base = 10  # any value > max column sum works; 10 keeps numbers small.
    total_digits = n + m

    numbers: List[int] = []

    # Helper to create a number from a digit list.
    def make_number(digits: List[int]) -> int:
        return _digits_to_int(digits, base)

    # Create true/false numbers for each variable.
    for var in range(1, m + 1):
        # Digits for true assignment.
        true_digits = [0] * total_digits
        false_digits = [0] * total_digits

        # Clause part.
        for clause_idx, clause in enumerate(clauses):
            if var in clause:
                # Positive literal +var appears.
                true_digits[clause_idx] = 1
            if -var in clause:
                false_digits[clause_idx] = 1

        # Variable part – column after the clauses.
        var_col = n + (var - 1)
        true_digits[var_col] = 1
        false_digits[var_col] = 1

        numbers.append(make_number(true_digits))
        numbers.append(make_number(false_digits))

    # Clause filler numbers (one per clause).
    for clause_idx in range(n):
        filler = [0] * total_digits
        filler[clause_idx] = 1
        numbers.append(make_number(filler))

    # Build target digits.
    target_digits = [0] * total_digits
    # Clause columns need sum 2 (one literal + filler).
    for clause_idx in range(n):
        target_digits[clause_idx] = 2
    # Variable columns need exactly one of true/false selected.
    for var in range(1, m + 1):
        target_digits[n + (var - 1)] = 1

    target = _digits_to_int(target_digits, base)

    return {"numbers": numbers, "target": target}

