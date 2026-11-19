"""Polynomial-time reduction from Partition to Subset Sum.

SOURCE: Partition   instance {"numbers": [a1, a2, ...]}
TARGET: Subset Sum  instance {"numbers": [a1, a2, ...], "target": t}

Reduction
---------
Let S = a1 + ... + an.

* If S is even, output the same numbers with target S/2.  A sub-list
  summing to S/2 leaves the complementary positions summing to S/2 as
  well, so this is exactly a balanced two-way partition.  Conversely any
  balanced partition gives a sub-list summing to S/2.

* If S is odd, no balanced partition can exist (two equal integer sums
  would make the total even).  Output the same numbers with target S+1,
  which is unreachable because the sum of all numbers is only S.  Hence
  the Subset Sum instance is a no-instance.

Edge cases are preserved: an empty list has S = 0 and maps to target 0
(yes, via the empty sub-list); zeros do not affect S or reachability.

The output is computed in O(n) arithmetic operations, so the reduction
runs in polynomial time and never invokes a solver.
"""


def reduce(instance):
    """Map a Partition instance to an equivalent Subset Sum instance."""
    numbers = list(instance["numbers"])
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # Unreachable: every sub-list sums to at most `total` < total + 1.
        target = total + 1

    return {"numbers": numbers, "target": target}
