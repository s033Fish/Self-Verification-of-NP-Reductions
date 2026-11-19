"""Polynomial-time reduction from Subset Sum to Partition.

SOURCE: SubsetSum  instance {"numbers": [...], "target": t}
TARGET: Partition  instance {"numbers": [...]}

Idea
----
Let S = sum(numbers).

If t < 0 or t > S the Subset Sum answer is "no"; we emit the Partition
instance {"numbers": [1]}, whose total (1) is odd, hence "no".

Otherwise a subset of ``numbers`` sums to t iff its complement sums to
S - t, so we may replace t by t' = min(t, S - t), which satisfies
0 <= t' <= S/2.  Emit the Partition instance

    numbers + [S - 2*t']

whose total is 2*(S - t'), i.e. half is S - t'.  A subset of this new
list summing to S - t' either omits the appended element (then a subset
of ``numbers`` sums to S - t', whose complement sums to t') or includes
it (then a subset of ``numbers`` sums to t').  In both cases a partition
exists iff a subset of ``numbers`` sums to t', i.e. iff the original
Subset Sum instance is a "yes".

The construction is linear time and all produced values are bounded by
the input values.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)

    # Definite "no" instances of Subset Sum: map to a definite "no"
    # Partition instance (total 1 is odd).
    if target < 0 or target > total:
        return {"numbers": [1]}

    # Subset sums to target iff it sums to total - target (complement).
    t = min(target, total - target)

    # Partition total = 2*(total - t), half = total - t.
    return {"numbers": numbers + [total - 2 * t]}
