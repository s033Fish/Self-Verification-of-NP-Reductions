"""Polynomial-time reduction from Subset Sum to Partition.

Source instance: {"numbers": [a1, a2, ...], "target": t}
Target instance: {"numbers": [b1, b2, ...]}

Construction
------------
Let S = sum(numbers).

* If t < 0, the source answer is always "no"; return a Partition
  instance with odd total, e.g. [1].
* If t > S, the source answer is always "no"; return [1].
* Otherwise 0 <= t <= S.  A subset of the original numbers sums to t
  exactly when its complement sums to S - t, so the answer only depends
  on t' = min(t, S - t), with 0 <= t' <= S/2.

  Add one extra number b = S - 2*t' (non-negative).  The resulting list
  has total S + (S - 2*t') = 2*(S - t'), so a partition must split it
  into two groups of sum S - t'.  Any such group either:
    * contains b, so the original elements in it sum to
      (S - t') - b = t'; or
    * does not contain b, so the original elements in it sum to
      S - t', and the complementary original elements sum to t'.
  In both cases a subset of the original numbers sums to t', hence also
  to t.  Conversely, if the original numbers have a subset summing to t',
  that subset together with b sums to S - t', yielding a partition.
  Therefore the target answer is yes iff the source answer is yes.

The construction uses only a sum and O(1) arithmetic, so it runs in
polynomial time.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]

    # Negative targets are always no; a single odd number is never
    # partitionable.
    if target < 0:
        return {"numbers": [1]}

    total = sum(numbers)

    # Targets larger than the total are always no.
    if target > total:
        return {"numbers": [1]}

    # Subset sums are complement-symmetric: sum t exists iff sum total-t
    # exists.  Work with the smaller of the two so the added element is
    # non-negative.
    reduced_target = min(target, total - target)

    extra = total - 2 * reduced_target
    return {"numbers": numbers + [extra]}
