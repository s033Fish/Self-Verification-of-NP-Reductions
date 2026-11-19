"""Polynomial-time reduction from Partition to Subset Sum.

Partition asks whether the positions of ``numbers`` can be split into two
groups of equal sum.  If the total sum is ``S``, that is possible exactly
when ``S`` is even and some subset of ``numbers`` sums to ``S // 2``.

Subset Sum asks whether some subset of ``numbers`` sums to ``target``, so
the reduction simply sets ``target = S // 2`` when ``S`` is even.  When
``S`` is odd Partition is always a no-instance; we then use the target
``S + 1``, which exceeds the sum of all (non-negative) numbers and is
therefore unreachable, giving a no-instance of Subset Sum.

The construction runs in linear time (dominated by computing the sum).
"""


def reduce(instance):
    """Reduce a Partition instance to a Subset Sum instance.

    ``instance`` is ``{"numbers": [a1, a2, ...]}`` and the returned value is
    ``{"numbers": [...], "target": t}``.  The returned instance is a
    yes-instance of Subset Sum exactly when the input is a yes-instance of
    Partition.
    """
    numbers = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 0:
        # Partition is yes iff a subset sums to exactly half the total.
        target = total // 2
    else:
        # Odd total: Partition is always no.  A target larger than the sum
        # of all numbers is unreachable, so Subset Sum is also no.
        target = total + 1

    return {"numbers": list(numbers), "target": target}
