"""Polynomial-time reduction from Subset Sum to Partition.

Source instance:  {"numbers": [a1, a2, ...], "target": t}
Target instance:  {"numbers": [b1, b2, ...]}

Let S = sum(numbers).  A subset of the numbers sums to t exactly when its
complement sums to S - t, so we may replace t by t' = min(t, S - t).
Then b = S - 2*t' is non-negative.  Appending b to the list gives total
S + b = 2*(S - t'), so a perfect partition must have one side summing to
S - t'.  Such a side exists iff the original numbers have a subset summing
to t' (equivalently, to t).
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]

    # t < 0 is always no; t > sum(numbers) is always no.
    if target < 0:
        return {"numbers": [1]}

    total = sum(numbers)

    if target > total:
        return {"numbers": [1]}

    # Subset sums are symmetric under complementation: a subset sums to
    # target iff its complement sums to total - target.  Pick the smaller
    # one so the appended number total - 2*t is non-negative.
    t = target
    if t > total - t:
        t = total - t

    extra = total - 2 * t
    return {"numbers": numbers + [extra]}
