"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}  (non-negative ints)
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Reduction:
    Let S = sum(numbers).
    * If S is even, use target = S // 2.  A subset summing to S/2 is
      exactly one side of an equal-sum partition (its complement is the
      other side), so the answers agree.
    * If S is odd, Partition is always a "no" instance.  Use target = S + 1,
      which exceeds the sum of all numbers and is therefore unreachable,
      giving a "no" Subset Sum instance.

Runs in O(n) time (just a sum over the input), so it is polynomial.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given Partition instance."""
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 0:
        target = total // 2
    else:
        # Odd total: Partition is always no; S + 1 is unreachable.
        target = total + 1
    return {"numbers": numbers, "target": target}
