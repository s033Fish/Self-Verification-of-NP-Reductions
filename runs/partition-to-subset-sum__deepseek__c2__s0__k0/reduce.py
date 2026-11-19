"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Let S = sum(numbers).  A valid partition into two equal-sum groups exists
iff S is even and some sub-list sums to S // 2.  Therefore:

* if S is odd, return a Subset Sum instance with target -1 (always no);
* otherwise return the same numbers with target S // 2.

This is computable in linear time (plus the size of the input list).
"""


def reduce(instance):
    """Reduce a Partition instance to a Subset Sum instance."""
    numbers = instance["numbers"]
    total = sum(numbers)

    if total % 2 != 0:
        # An odd total can never be split into two equal-sum groups.
        # Subset Sum with a negative target is always no.
        return {"numbers": list(numbers), "target": -1}

    # Even total: an equal partition is exactly a sub-list summing to half.
    return {"numbers": list(numbers), "target": total // 2}
