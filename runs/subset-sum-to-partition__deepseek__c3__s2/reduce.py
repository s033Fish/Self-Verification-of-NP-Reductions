"""Polynomial-time reduction from Subset Sum to Partition.

Given a Subset Sum instance ``{"numbers": [...], "target": t}`` with
``S = sum(numbers)``, the reduction works as follows.

* ``t < 0`` or ``t > S``: the answer is no; emit a trivially-no Partition
  instance (an odd total).
* Otherwise let ``t' = min(t, S - t)``.  A subset of the numbers sums to
  ``t`` iff some subset sums to ``t'`` (complementing handles the
  ``t' = S - t`` case).  Add one extra number ``b = S - 2*t' >= 0``.

The resulting list has total ``2*(S - t')``, so a balanced partition has
each side equal to ``S - t'``.  Such a partition exists iff the original
numbers contain a subset summing to ``t'`` (either the side containing
``b`` leaves ``t'`` on the other side, or the side without ``b`` is
itself that subset).  Hence the Partition instance is yes exactly when
the Subset Sum instance is yes.

The construction is linear in the input size, hence polynomial time.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)

    # Negative targets are always no; targets above the total are no too.
    if target < 0 or target > total:
        return {"numbers": [1]}

    # Reduce to the smaller of target and its complement.
    t = min(target, total - target)

    # Extra element makes the two partition halves equal.
    extra = total - 2 * t
    return {"numbers": numbers + [extra]}
