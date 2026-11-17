"""Polynomial-time reduction from Subset Sum to Partition.

SOURCE (Subset Sum): {"numbers": [a1, ...], "target": t}
    Yes iff some sub-list sums to exactly t.

TARGET (Partition): {"numbers": [a1, ...]}
    Yes iff the positions split into two groups of equal sum.

Reduction
---------
Let S = sum(numbers).

* t < 0  -> always no.
* t > S  -> always no (no subset can exceed the total).
* otherwise set t' = min(t, S - t).  A subset sums to t iff some subset
  sums to t' (for t' = S - t use the complement bijection).
  Since t' <= S/2, b = S - 2t' >= 0.  Return numbers + [b].

The new total is S + b = 2(S - t'), so a partition needs a subset summing
to S - t'.  A subset of the new list either:
  * avoids b: sums to S - t' using originals, whose complement sums to t'; or
  * includes b: the originals part sums to (S - t') - b = t'.
Either way it is equivalent to "some subset of the originals sums to t'",
i.e. to the original Subset Sum instance being yes.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    t = instance["target"]
    S = sum(numbers)

    # Trivially-no cases: return an odd-total (hence unpartitionable) list.
    if t < 0 or t > S:
        return {"numbers": [1]}

    # Subset sums to t iff subset sums to S - t; pick the smaller target so
    # that the padding element b = S - 2*t' is non-negative.
    t_prime = min(t, S - t)
    b = S - 2 * t_prime
    return {"numbers": numbers + [b]}
