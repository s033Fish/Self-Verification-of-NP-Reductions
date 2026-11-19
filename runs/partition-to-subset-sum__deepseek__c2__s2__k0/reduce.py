"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Let S = sum(numbers).

* If S is even, the partition is yes exactly when some subset sums to S/2,
  because the remaining elements then also sum to S/2.  So map to
  {"numbers": numbers, "target": S // 2}.
* If S is odd, no partition can be balanced, so the answer must be no.
  Since every number is non-negative and their total is S, no subset can
  sum to S + 1; map to {"numbers": numbers, "target": S + 1}, which is
  always a no-instance of Subset Sum.

The construction only computes a sum and copies the list, so it runs in
polynomial time (indeed linear time in the input size).
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 0:
        return {"numbers": numbers, "target": total // 2}
    return {"numbers": numbers, "target": total + 1}
