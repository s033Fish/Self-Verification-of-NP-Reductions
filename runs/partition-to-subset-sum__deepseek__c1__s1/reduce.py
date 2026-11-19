"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Let T = sum(numbers).  Partition is yes iff T is even and some sub-list
of the numbers sums to exactly T/2.

* If T is even, use target = T/2.  A sub-list summing to T/2 exists iff
  the remaining positions sum to T/2 as well, i.e. the positions can be
  split into two equal-sum groups.
* If T is odd, Partition is always no.  Use target = T + 1, which is
  strictly larger than the sum of all numbers, so no sub-list can reach
  it (Subset Sum is then no as well).

The reduction only computes the sum and copies the list, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 0:
        target = total // 2
    else:
        target = total + 1
    return {"numbers": numbers, "target": target}
