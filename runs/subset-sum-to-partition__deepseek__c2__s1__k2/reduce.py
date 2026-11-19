"""Polynomial-time reduction from Subset Sum to Partition.

Source instance: {"numbers": [a1, a2, ...], "target": t}
Target instance: {"numbers": [b1, b2, ...]}

Reduction
---------
If t < 0, Subset Sum is always "no"; emit [1] (odd total => Partition "no").

Otherwise let S = sum(numbers) and add one extra number
    b = |S - 2t|
so the target list is numbers + [b].

Correctness
-----------
Let T = S + b.

Case S >= 2t:  b = S - 2t, T = 2(S - t), half = S - t.
    A partition exists iff one side contains b together with a subset of
    the original numbers summing to (S - t) - (S - 2t) = t.  So yes iff a
    subset of the original numbers sums to t.

Case S < 2t:   b = 2t - S, T = 2t, half = t.
    Since b > t whenever t > S, no partition exists when t > S (which is
    correct: no subset can reach t).  When t <= S, a partition must put b
    on one side, requiring the original numbers on that side to sum to
    t - (2t - S) = S - t; equivalently the other side sums to t.  So yes
    iff a subset of the original numbers sums to t.

In both cases the constructed Partition instance is "yes" exactly when the
Subset Sum instance is "yes".  The construction is linear time.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # t < 0 is always "no"; [1] has odd total, hence Partition is "no".
    if target < 0:
        return {"numbers": [1]}

    total = sum(numbers)
    extra = abs(total - 2 * target)
    return {"numbers": list(numbers) + [extra]}
