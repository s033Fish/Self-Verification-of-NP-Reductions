"""Reduction from 3‑SAT to Subset Sum.

We implement the standard Karp reduction using a mixed‑radix (base) encoding.
For a formula with ``m`` variables and ``k`` clauses we construct numbers
representing literals and auxiliary *clause‑adjuster* numbers.  The construction
ensures:

* Exactly one literal per variable must be selected (to satisfy the variable
  digit of the target).
* For each clause the sum of the selected literal digits plus the digit of the
  chosen clause‑adjuster equals the target digit ``1``.  Because the base is
  larger than the maximum possible sum, no carries occur and the equality of the
  digits is equivalent to the SAT condition.

The reduction runs in time polynomial in ``m`` and ``k`` and produces a
polynomial‑size Subset‑Sum instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, SubsetSum

# Base must be larger than the maximum digit sum that can appear in any position.
# In a clause at most three literals contribute a ``1`` each, so the sum is ≤3.
# We also need digits ``base‑2`` and ``base‑1`` for the clause‑adjusters.
BASE = 4  # > 3, and provides digits 0,1,2,3.


def _digits_to_int(digits: List[int]) -> int:
    """Convert a list of ``BASE``‑digits (least‑significant first) to an int."""
    value = 0
    mult = 1
    for d in digits:
        value += d * mult
        mult *= BASE
    return value


def reduce(instance: Dict) -> Dict:
    """Polynomial‑time reduction from 3‑SAT to Subset Sum.

    Returns a Subset‑Sum instance whose answer matches the answer of the given
    3‑SAT instance.
    """
    # Validate the source instance.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k: int = len(clauses)

    numbers: List[int] = []

    # ----- Literal numbers -----
    # Map each literal to the list of clause indices it appears in.
    literal_to_clauses: dict[tuple[int, bool], List[int]] = {}
    for var in range(1, m + 1):
        literal_to_clauses[(var, True)] = []
        literal_to_clauses[(var, False)] = []
    for idx, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit)
            sign = lit > 0
            literal_to_clauses[(var, sign)].append(idx)

    # Create a number for each literal.
    for var in range(1, m + 1):
        for sign in (True, False):
            digits = [0] * (k + m)  # first k clause digits, then m variable digits
            # Variable digit (position k + var - 1) is 1.
            digits[k + var - 1] = 1
            # Clause digits where this literal appears are set to 1.
            for clause_idx in literal_to_clauses[(var, sign)]:
                digits[clause_idx] = 1
            numbers.append(_digits_to_int(digits))

    # ----- Clause‑adjuster numbers -----
    # For each clause we add four numbers with a digit 0,1,2,3 respectively at the
    # clause position and 0 elsewhere.  The subset solver will pick the one that
    # makes the total digit equal to the target digit 1.
    for clause_idx in range(k):
        for d in range(BASE):  # 0,1,2,3
            digits = [0] * (k + m)
            digits[clause_idx] = d
            numbers.append(_digits_to_int(digits))

    # ----- Target number -----
    # Digit 1 for every clause and every variable.
    target_digits = [1] * (k + m)
    target = _digits_to_int(target_digits)

    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

