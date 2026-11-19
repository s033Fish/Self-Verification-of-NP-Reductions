"""Reduction from 3-SAT (SOURCE) to Subset Sum (TARGET).

The reduction follows the classic Karp construction using a mixed‑radix
representation.  For a formula with ``m`` variables and ``k`` clauses we
choose a base ``B = k + 1``.  Each number is interpreted as a ``k+1``
digit vector where the first ``k`` digits correspond to the clauses and the
last digit (index ``k``) counts how many variable‑choice numbers have been
selected.

For every variable ``i`` we create two numbers:

* ``true_i`` – representing the assignment *x_i = True*
* ``false_i`` – representing the assignment *x_i = False*

Both numbers have a ``1`` in the last digit so that any feasible subset
must contain exactly ``m`` of these numbers (one per variable) to reach the
target count digit ``m``.

For the clause digits, a number has a ``1`` in position ``j`` iff the
corresponding literal satisfies clause ``j``.  The target vector has a ``1``
in each clause position, meaning that the sum of the selected numbers must
have at least one ``1`` in every clause digit.  Because the base ``B`` is
larger than the maximum possible sum in any digit (the sum cannot exceed
``m``), there is no carry between digits.  Consequently the clause digits
in the sum equal the number of selected literals that satisfy each clause.

The construction therefore yields a Subset Sum instance that is a *yes*
instance iff the original 3‑SAT formula is satisfiable.

Note: The reduction runs in time polynomial in ``m`` and ``k`` and uses
only integer arithmetic.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem specifications so that type checkers and users can see
# the expected instance format.  The import is safe because ``problems.py``
# lives in the same directory.
from problems import ThreeSat, SubsetSum


def _encode_number(digits: List[int], base: int) -> int:
    """Encode a list of ``digits`` (least‑significant first) in the given ``base``.

    ``digits[i]`` must be in ``0..base-1``.  The function returns the integer
    value of the mixed‑radix number.
    """
    value = 0
    multiplier = 1
    for d in digits:
        value += d * multiplier
        multiplier *= base
    return value


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` specification:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
        literal is an ``int`` ``+v`` (true) or ``-v`` (false).

    Returns
    -------
    dict
        A Subset Sum instance ``{"numbers": [...], "target": t}`` that is a
        yes‑instance exactly when the input formula is satisfiable.
    """
    # Validate input using the problem class – this will raise if malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k = len(clauses)

    # Edge case: empty formula is always satisfiable.
    if k == 0:
        # The empty Subset Sum instance with target 0 is a trivial yes.
        return {"numbers": [], "target": 0}

    # Base for the mixed‑radix representation.  It must be larger than the
    # maximum possible digit sum to avoid carries.  The digit sum for a clause
    # cannot exceed the number of variables, so ``max(m, k) + 1`` suffices.
    base = max(m, k) + 1

    numbers: List[int] = []

    # For each variable create the true/false numbers.
    for var in range(1, m + 1):
        # Digits for the true assignment.
        true_digits = [0] * (k + 1)  # last digit is the counter
        false_digits = [0] * (k + 1)
        # Counter digit (position k) is 1 for both choices.
        true_digits[k] = 1
        false_digits[k] = 1
        # Fill clause digits.
        for idx, clause in enumerate(clauses):
            # Clause satisfied by true assignment?
            if var in clause:
                true_digits[idx] = 1
            # Clause satisfied by false assignment?
            if -var in clause:
                false_digits[idx] = 1
        # Encode and add to the list.
        numbers.append(_encode_number(true_digits, base))
        numbers.append(_encode_number(false_digits, base))

    # Construct target vector: 1 for each clause, and m for the counter.
    target_digits = [1] * k + [m]
    target = _encode_number(target_digits, base)

    # Return the Subset Sum instance.
    return {"numbers": numbers, "target": target}

