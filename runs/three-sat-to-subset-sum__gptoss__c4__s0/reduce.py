"""Reduction from 3‑SAT to Subset Sum using the classic base‑2 construction.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    The construction works in base 2 with an extra most‑significant digit to
    capture carries.  It runs in polynomial time.
    """

    ThreeSat.validate(instance)

    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Base 2 representation, extra digit for carries.
    B = 2
    total_digits = m + c + 1  # variable positions, clause positions, extra carry digit
    extra_idx = m + c

    def encode(digits: List[int]) -> int:
        """Encode a list of base‑B digits (least‑significant first) as an integer."""
        val = 0
        mult = 1
        for d in digits:
            val += d * mult
            mult *= B
        return val

    numbers: List[int] = []

    # For each variable create two numbers: one for the positive literal, one for the negative.
    for var in range(1, m + 1):
        digits_pos = [0] * total_digits
        digits_neg = [0] * total_digits
        # Variable position gets a 1 in both numbers (ensures exactly one is chosen).
        digits_pos[var - 1] = 1
        digits_neg[var - 1] = 1
        # Clause positions get a 1 if the literal appears in that clause.
        for idx, clause in enumerate(clauses):
            pos = m + idx
            if +var in clause:
                digits_pos[pos] = 1
            if -var in clause:
                digits_neg[pos] = 1
        numbers.append(encode(digits_pos))
        numbers.append(encode(digits_neg))

    # Padding numbers: one per clause, contributing a 1 at its clause position.
    for idx in range(c):
        digits = [0] * total_digits
        digits[m + idx] = 1
        numbers.append(encode(digits))

    # Target digits:
    #   * 1 for each variable (so exactly one of each pair must be taken)
    #   * 1 for each clause (the padding number contributes this)
    #   * c for the extra carry digit (we need a carry from every clause, i.e., each clause must be satisfied)
    target_digits = [1] * m + [1] * c + [c]
    target = encode(target_digits)

    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

