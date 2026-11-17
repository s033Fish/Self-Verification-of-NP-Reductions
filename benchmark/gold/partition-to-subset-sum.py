"""Gold reduction: Partition -> Subset Sum.          [difficulty: 1 of 6]

SOURCE  Partition   {"numbers": [a1, a2, ...]}
        yes iff the positions split into two groups with equal sums.
TARGET  Subset Sum  {"numbers": [a1, a2, ...], "target": t}
        yes iff some sub-list sums to exactly t.

Construction
  1. Let S be the sum of the numbers.
  2. A partition exists exactly when some sub-list sums to S / 2 (the rest of
     the numbers then sum to S / 2 as well).
  3. So: keep the same numbers, target = S / 2.
"""


def reduce(instance):
    numbers = instance["numbers"]
    total = sum(numbers)

    if total % 2 != 0:
        return {"numbers": [], "target": 1}

    return {"numbers": numbers, "target": total // 2}
