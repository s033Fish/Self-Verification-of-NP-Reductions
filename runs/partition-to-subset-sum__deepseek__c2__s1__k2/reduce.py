"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

A Partition instance is yes exactly when some subset of its numbers sums to
half of the total sum.  If the total is odd, Partition is immediately no;
in that case we return a Subset Sum instance whose target is larger than the
sum of all numbers, which is also immediately no (all numbers are
non-negative).
"""


def reduce(instance):
    """Reduce a Partition instance to a Subset Sum instance.

    The returned instance is yes iff the input Partition instance is yes.
    """
    numbers = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 0:
        return {"numbers": list(numbers), "target": total // 2}

    # Odd total: Partition is no.  Asking for more than the sum of all
    # numbers is impossible, so the Subset Sum instance is no as well.
    return {"numbers": list(numbers), "target": total + 1}
