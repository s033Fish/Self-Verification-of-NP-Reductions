"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Let S = sum(numbers).  Partition is yes exactly when S is even and some
sub-list of numbers sums to S/2.  So:
  * if S is even, use the same numbers with target = S/2;
  * if S is odd, Partition is always no, so return an instance that is
    always no: target = -1 (Subset Sum with a negative target is never yes).
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 != 0:
        # Partition is definitely no; Subset Sum with target -1 is definitely no.
        return {"numbers": numbers, "target": -1}
    return {"numbers": numbers, "target": total // 2}
