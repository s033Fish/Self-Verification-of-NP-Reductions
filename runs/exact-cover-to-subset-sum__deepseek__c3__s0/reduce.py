"""Polynomial-time reduction from Exact Cover to Subset Sum.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
Subset Sum instance:  {"numbers": [a1, a2, ...], "target": t}

Construction
------------
Let m be the number of sets and choose a base b = max(2, m + 1).

For each set S_i build the integer

    n_i = sum over e in S_i of b**e

so that the base-b digit at position e of n_i is 1 exactly when element e
belongs to S_i (and 0 otherwise).  Let the target be

    t = sum over e = 0..u-1 of b**e

whose base-b representation is 1 in every element position.

A sub-list of the n_i sums to t iff, for every element position e, exactly
one chosen set contains e.  Indeed the digit at position e of the sum is the
number of chosen sets containing e; it must equal 1.  No carries can occur
because at most m sets are chosen, so every digit column is at most m < b.

Hence the Subset Sum instance is yes exactly when the Exact Cover instance
is yes.

Edge cases
----------
* u = 0: t = 0, so the empty sub-list works (always yes), matching the
  source edge case.
* Empty sets: they map to the number 0, which never changes a sum, so they
  never matter, matching the source edge case.
* Duplicate non-empty sets: choosing both copies would put a 2 in every
  element position they share, which cannot equal the target's 1, so they
  can never both be chosen, matching the source edge case.
* No sets (m = 0): base is 2 and the number list is empty; the target is 0
  only when u = 0, otherwise it is positive and unreachable.

The construction is polynomial: it produces m numbers of O(u * log m) bits,
i.e. O(m * u * log m) bits total, polynomial in the input size.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    base = max(2, len(sets) + 1)
    powers = [base ** e for e in range(universe_size)]

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)
    return {"numbers": numbers, "target": target}
