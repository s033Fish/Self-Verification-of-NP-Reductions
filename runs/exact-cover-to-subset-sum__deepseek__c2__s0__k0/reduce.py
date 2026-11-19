"""Polynomial-time reduction from Exact Cover to Subset Sum.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
Subset Sum instance:  {"numbers": [a1, a2, ...], "target": t}

Construction
------------
Let m = len(sets) and choose the base B = m + 1.  Represent a subset of the
universe 0..u-1 by the integer whose base-B digit e is 1 exactly when element
e belongs to the subset.  For every input set S create the number

    a(S) = sum_{e in S} B^e

and let the target be the integer with a 1 in every one of the u digits:

    t = sum_{e=0}^{u-1} B^e.

Correctness
-----------
A chosen sub-list of the numbers corresponds to a chosen collection of sets.
Its value is sum_e c_e * B^e, where c_e is the number of chosen sets that
contain element e.  Since at most m sets are chosen, 0 <= c_e <= m < B, so
this is the canonical base-B expansion and there are no carries.  The target
has canonical digits all equal to 1, hence the sum equals t iff c_e = 1 for
every element e, i.e. the chosen sets are pairwise disjoint and cover the
whole universe.  Thus the Subset Sum answer is yes exactly when the Exact
Cover answer is yes.

Edge cases
----------
* u = 0: the target is 0, and Subset Sum with target 0 is always yes, matching
  the empty exact cover.
* Empty input sets become the number 0; they can be included or omitted and
  never change the sum, matching the fact that empty sets never matter.
* Two copies of the same non-empty set give two equal numbers; choosing both
  would put a digit count of 2 in some position, which cannot equal the target
  digit 1, so they can never both be used.
* m = 0: B = 1; the numbers list is empty and the target is u, which is yes
  only for u = 0.

The construction uses O(u + sum |S|) arithmetic on integers of O(u log m)
bits, hence runs in time polynomial in the input size.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    m = len(sets)
    base = m + 1

    # powers[e] = base ** e, for e = 0 .. universe_size - 1
    powers = [1] * universe_size
    for e in range(1, universe_size):
        powers[e] = powers[e - 1] * base

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)

    return {"numbers": numbers, "target": target}
