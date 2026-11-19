"""Polynomial-time reduction from Exact Cover to Subset Sum.

Exact Cover instance:
    {"universe_size": u, "sets": [[element, ...], ...]}
Subset Sum instance:
    {"numbers": [a1, a2, ...], "target": t}

Construction
------------
Let m be the number of sets and choose the base b = max(2, m + 1).
Represent the universe element e by the digit position e in base b.

* For every set S_j create a number whose base-b digit at position e is 1
  if e is in S_j and 0 otherwise:
        a_j = sum(b ** e for e in S_j)
* The target is the number with a 1 in every universe position:
        t = sum(b ** e for e in range(u))

Correctness
-----------
Any chosen sub-list uses at most m numbers, and each number has base-b digits
in {0, 1}.  Hence the digit sum in any position is at most m = b - 1 < b, so
adding the chosen numbers never produces a carry.  Consequently the sum equals
t exactly when every digit position sums to 1, i.e. every universe element is
contained in exactly one chosen set: the chosen sets are pairwise disjoint and
their union is the whole universe.  That is precisely an exact cover.

Empty sets become the number 0 and cannot help or hurt.  Two copies of the
same non-empty set would put a 2 in some digit position, which (carry-free)
cannot equal the target, so they can never both be chosen.  For u = 0 the
target is 0, and the empty sub-list is a valid solution, matching the yes
answer for the empty universe.

The construction uses O(u * log m) bit operations per set and so runs in
polynomial time in the size of the input.
"""


def reduce(instance):
    """Reduce an Exact Cover instance to a Subset Sum instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    # A base larger than the number of sets guarantees carry-free addition.
    base = max(2, len(sets) + 1)

    # powers[e] = base ** e, for every universe element e.
    powers = [1] * universe_size
    for e in range(1, universe_size):
        powers[e] = powers[e - 1] * base

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)  # base-b number 11...1 with u ones (0 when u == 0)

    return {"numbers": numbers, "target": target}
