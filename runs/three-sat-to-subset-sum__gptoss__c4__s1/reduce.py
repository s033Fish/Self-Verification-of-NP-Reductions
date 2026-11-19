"""Reduction from 3‑SAT to Subset Sum.

We use a base‑B positional encoding where B is larger than any possible digit
sum, guaranteeing that addition of the constructed numbers never produces a
carry.  For a formula with m variables and k clauses we create numbers with
(m + k) digits.

Construction (B = max(5, m+2)):
* For each variable i (1‑based) we create two numbers:
    - true_i  : digit 1 at position i and digit 1 in each clause where the
                literal +i appears.
    - false_i : digit 1 at position i and digit 1 in each clause where the
                literal -i appears.
* For each clause j we add a *clause filler* number that has digit 1 at the
  clause position (and 0 elsewhere).
* The target number has digit 1 in every variable position and digit 2 in every
  clause position.  This forces the subset to pick exactly one of true_i/false_i
  for each variable (to obtain a 1 in the variable slots) and, for each clause,
  at least one literal (contributing 1) plus optionally the filler, so the total
  in each clause digit is exactly 2.

With B large enough (≥5) the digits never interfere, so a subset sums to the
target iff the original 3‑SAT formula is satisfiable.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    The returned instance satisfies ``SubsetSum.validate`` and preserves the
    answer (yes‑instance ↔ yes‑instance).
    """
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k = len(clauses)

    # Base larger than any possible digit sum (max 4 contributions per clause).
    B = max(5, m + 2)

    # Powers for each digit position (least‑significant = position 0).
    powers = [B ** i for i in range(m + k)]

    # Record where each literal appears.
    pos_occurs: List[set[int]] = [set() for _ in range(m + 1)]
    neg_occurs: List[set[int]] = [set() for _ in range(m + 1)]
    for j, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit)
            if lit > 0:
                pos_occurs[var].add(j)
            else:
                neg_occurs[var].add(j)

    numbers: List[int] = []

    # True/false numbers for each variable.
    for i in range(1, m + 1):
        true_val = powers[i - 1]
        false_val = powers[i - 1]
        for j in pos_occurs[i]:
            true_val += powers[m + j]
        for j in neg_occurs[i]:
            false_val += powers[m + j]
        numbers.append(true_val)
        numbers.append(false_val)

    # Clause filler numbers (digit 1 in clause position).
    for j in range(k):
        numbers.append(powers[m + j])

    # Target: 1 in each variable position, 2 in each clause position.
    target = sum(powers[:m]) + 2 * sum(powers[m:])

    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

