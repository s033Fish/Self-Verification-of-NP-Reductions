"""Polynomial-time reduction from Subset Sum to Partition.

Source instance:  {"numbers": [a1, ..., an], "target": t}
Target instance:  {"numbers": [b1, ..., bm]}

Reduction idea
--------------
Let S = sum(numbers).  If t < 0 or t > S the Subset Sum answer is no
(all numbers are non-negative), so we emit a trivially-no Partition
instance (a single 1 has odd total).

Otherwise, because a subset sums to t iff its complement sums to S - t,
we may replace t by t' = min(t, S - t), so that 0 <= t' <= S/2.

Now add one extra number x = S - 2*t' >= 0.  The new total is

    S + x = 2*S - 2*t' = 2*(S - t'),

so a valid partition must select a subset of the new numbers summing to
S - t'.  Such a subset either

  * contains x: then the rest of the subset is a sub-list of the original
    numbers summing to (S - t') - x = t', or
  * does not contain x: then it is a sub-list summing to S - t', whose
    complement in the original numbers sums to t'.

Thus a partition exists exactly when some sub-list of the original numbers
sums to t', which (by the complement argument) is equivalent to some
sub-list summing to t.  This is precisely the Subset Sum answer.

The construction only computes a sum, a minimum and copies the list, so it
runs in polynomial time.  No brute-force solver is invoked.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    total = sum(numbers)

    # Negative targets and targets above the total are always "no".
    if target < 0 or target > total:
        # A single odd number has odd total, so Partition is "no".
        return {"numbers": [1]}

    # Subset sums to target iff the complementary subset sums to total-target.
    reduced_target = min(target, total - target)

    extra = total - 2 * reduced_target  # non-negative because t' <= total/2

    return {"numbers": list(numbers) + [extra]}
