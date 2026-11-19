"""Polynomial-time reduction from Exact Cover to Subset Sum.

Exact Cover instance: {"universe_size": u, "sets": [[e, ...], ...]}
Subset Sum instance:  {"numbers": [a1, a2, ...], "target": t}

Encoding
--------
Pick a base B strictly larger than the number of sets (and at least 2).
Represent a subset of the universe by the integer whose base-B digit at
position e is 1 when element e is present and 0 otherwise.  For every set S
emit the number  sum_{e in S} B**e.  The target is  sum_{e=0}^{u-1} B**e,
i.e. the integer with digit 1 in every one of the u positions.

Because every set contributes at most one unit to any digit and at most
len(sets) < B sets are available, adding chosen numbers never produces a
carry.  Hence a sub-list sums to the target iff, digit by digit, every
element is covered exactly once: the chosen sets form an exact cover.

Edge cases:
  * u = 0: target is 0, which is always reachable (empty sub-list) -> yes.
  * empty sets: contribute the number 0, which never changes a sum.
  * duplicated non-empty sets: taking both would make some digit >= 2,
    which cannot equal the all-ones target, so they are never both chosen.
  * no sets: B = 2, target has the correct all-ones representation.

The construction is polynomial: the numbers and target have O(u log B)
bits, and there is one number per input set.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    base = max(2, len(sets) + 1)

    powers = [base ** e for e in range(universe_size)]

    numbers = []
    for s in sets:
        value = 0
        for e in s:
            value += powers[e]
        numbers.append(value)

    target = sum(powers)

    return {"numbers": numbers, "target": target}
