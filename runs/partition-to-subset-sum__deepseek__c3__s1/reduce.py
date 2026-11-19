"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

A Partition instance with total sum S is yes iff some sub-list sums to
S/2 (the chosen sub-list is one of the two equal-sum groups).  So for
even S we simply ask Subset Sum for target S//2 on the same numbers.

If S is odd, Partition is always no.  Subset Sum is always no for a
negative target (the empty sub-list only reaches 0), so we map odd-S
instances to the trivially-no instance {"numbers": [], "target": -1}.
This is a valid Subset Sum instance and keeps the reduction total and
correct on every input, including the empty list (S = 0, target = 0,
which is yes for both).
"""


def reduce(instance):
    """Return a Subset Sum instance yes iff the Partition instance is yes."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        # Partition is always no for an odd total; t < 0 is always no.
        return {"numbers": [], "target": -1}
    return {"numbers": list(numbers), "target": total // 2}
