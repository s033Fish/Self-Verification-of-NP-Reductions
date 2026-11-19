"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Let S = sum(numbers).

* If S is even, Partition is yes iff some sub-list sums to S/2, so we
  output the same numbers with target S/2.
* If S is odd, Partition is always no.  No sub-list can sum to more than
  S, so target S + 1 is unreachable; we output target S + 1.

This is a valid reduction: the answer is preserved in both cases, and the
construction only computes a sum and a comparison, so it runs in time
polynomial in the size of the instance.
"""


def reduce(instance):
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 0:
        target = total // 2
    else:
        target = total + 1
    return {"numbers": list(numbers), "target": target}
