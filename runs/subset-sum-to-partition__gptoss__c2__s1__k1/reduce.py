"""Reduction from Subset Sum to Partition.

Given an instance of Subset Sum:
    {"numbers": [a1, a2, ...], "target": t}
we construct an instance of Partition:
    {"numbers": [b1, b2, ...]}
such that the Partition instance is a YES-instance iff the original
Subset Sum instance is a YES-instance.

The construction follows the classic reduction:
    Let S = sum(a_i).  Define x = S - 2*t (which is non‑negative when
    0 <= t <= S).  The new list is the original numbers together with x.
    The total sum becomes 2*(S - t), so each partition side must sum to
    S - t.  One side can contain the complement of a subset summing to t,
    the other side contains that subset together with x.

Edge cases are handled explicitly:
* t == 0 → always YES for Subset Sum; we return the empty list, which is
  a YES‑instance of Partition.
* t < 0 or t > S → Subset Sum is a NO‑instance; we return a list with a
  single element [1] (odd total) which is a NO‑instance of Partition.
* The construction guarantees all numbers are non‑negative integers.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict with keys "numbers" (list of non‑negative ints) and
        "target" (int).

    Returns
    -------
    dict with key "numbers" suitable for the Partition problem.
    """
    numbers: List[int] = list(instance.get("numbers", []))
    t: int = int(instance.get("target", 0))

    # Edge case: target zero -> always YES. Return empty list (YES for Partition).
    if t == 0:
        return {"numbers": []}

    total = sum(numbers)

    # Cases where Subset Sum is definitely NO.
    if t < 0 or t > total:
        # Return a Partition instance that is trivially NO: odd total sum.
        return {"numbers": [1]}

    # Classic reduction requires a non‑negative extra element.
    # Ensure the extra element x = total - 2*t_adj is non‑negative.
    # We may replace t by its complement (total - t) if that yields a
    # smaller non‑negative value, preserving the YES/NO answer.
    t_adj = t if t <= total - t else total - t
    x = total - 2 * t_adj
    new_numbers = numbers + [x]
    return {"numbers": new_numbers}

