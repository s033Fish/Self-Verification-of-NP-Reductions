"""Polynomial-time reduction from Partition to Subset Sum.

Partition asks whether the numbers can be split into two groups of equal
sum.  If the total sum is S, this is equivalent to asking whether some
subset sums to S/2.  Thus:

* if S is even, use the same numbers with target S/2;
* if S is odd, Partition is always false, so use target -1, which is
  always false for Subset Sum.

Both cases run in time linear in the input size (dominated by summing the
numbers), so the reduction is polynomial-time.
"""


def reduce(instance):
    """Reduce a Partition instance to a Subset Sum instance."""
    numbers = list(instance["numbers"])
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total: Partition is unsatisfiable.  A negative target is
        # always unsatisfiable for Subset Sum.
        return {"numbers": numbers, "target": -1}

    return {"numbers": numbers, "target": total // 2}
