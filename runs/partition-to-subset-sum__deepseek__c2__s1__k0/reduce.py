"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, ..., an]}.
Let S = sum(numbers).

If S is odd, Partition is always a no-instance.  We map to a fixed
no-instance of Subset Sum (empty list, negative target).

If S is even, Partition is yes iff some sub-list sums to S/2, because the
remaining positions then automatically sum to S - S/2 = S/2.  So we map to
{"numbers": numbers, "target": S // 2}.

The reduction runs in linear time (computing the sum) and does not solve
either problem.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 != 0:
        # Odd total: Partition is always no.  Return a guaranteed no-instance
        # of Subset Sum (empty list with a negative target).
        return {"numbers": [], "target": -1}
    return {"numbers": numbers, "target": total // 2}
