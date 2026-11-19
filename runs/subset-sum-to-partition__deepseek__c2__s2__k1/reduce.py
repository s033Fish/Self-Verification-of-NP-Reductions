"""Polynomial-time reduction from Subset Sum to Partition.

Source instance:
    {"numbers": [a1, a2, ...], "target": t}

Target instance:
    {"numbers": [b1, b2, ...]}

Reduction:
    Let S = sum(numbers) and b = abs(S - 2*t).
    Return {"numbers": numbers + [b]}.

Correctness:
    A partition of the new list into two equal-sum groups has half-sum
    H = (S + b) / 2.  The added element b forces the original numbers to
    contain a subset summing to t exactly when such a partition exists.
"""


def reduce(instance):
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]

    total = sum(numbers)
    extra = abs(total - 2 * target)

    return {"numbers": numbers + [extra]}
