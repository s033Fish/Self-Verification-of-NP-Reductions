"""Polynomial-time reduction from Exact Cover to Subset Sum.

Source (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}
    Universe is 0..u-1.  Yes iff some of the sets are pairwise disjoint
    and their union is exactly the universe.

Target (Subset Sum):
    {"numbers": [a1, a2, ...], "target": t}
    Yes iff some sub-list of numbers sums to exactly t.

Reduction
---------
Let m = number of sets and choose base b = m + 1.  For every set S build a
number whose base-b representation has
    * digit 1 in position e for each element e in S, and
    * digit 1 in the extra "top" position u.
Add m filler numbers, each equal to b**u (a 1 in the top position only).
The target has digit 1 in every element position 0..u-1 and digit m in the
top position.

If k sets form an exact cover, choosing those k set-numbers together with
m - k fillers gives digit 1 in every element position and digit m on top,
i.e. exactly the target.  Conversely, in any solution every element digit
sums to exactly 1: each digit is a sum of at most m ones, hence < b = m+1,
so there is no carry, and the target digit is 1.  The top digit must sum to
m, so the chosen set-numbers are pairwise disjoint and cover the universe,
i.e. they are an exact cover.  The construction uses O(m) numbers with
O(u * log m) bits each, so it runs in polynomial time.
"""


def reduce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)

    # No sets available: yes iff the universe is empty.
    if m == 0:
        return {"numbers": [], "target": 0 if u == 0 else 1}

    base = m + 1
    top = base ** u

    powers = [base ** e for e in range(u)]

    numbers = []
    for s in sets:
        value = top
        for e in s:
            value += powers[e]
        numbers.append(value)

    # m fillers: each contributes only to the top digit.
    numbers.extend([top] * m)

    target = m * top + sum(powers)
    return {"numbers": numbers, "target": target}
