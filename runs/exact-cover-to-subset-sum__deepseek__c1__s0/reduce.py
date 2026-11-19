"""Polynomial-time reduction from Exact Cover to Subset Sum.

Exact Cover instance:
    {"universe_size": u, "sets": [[element, ...], ...]}

Subset Sum instance:
    {"numbers": [a1, a2, ...], "target": t}

Construction
------------
Let m be the number of sets and choose base B = m + 1.  For each element
e in 0..u-1 use B**e as its place value.  Map every set S to the number

    value(S) = sum(B**e for e in S)

and map the universe to the target

    target = sum(B**e for e in 0..u-1).

Because at most m of the chosen numbers can contribute to any one place
value, each digit of a sum of chosen values lies in 0..m < B: there are no
carries between place values.  Hence a sub-list sums to the target exactly
when, for every element e, exactly one chosen set contains e.  That is
precisely an exact cover.  Empty sets become the number 0 and are harmless,
and duplicate sets simply give duplicate numbers, of which at most one can
be used in a valid exact cover.

The numbers and target have O(u * log(m + 1)) bits, so the construction
runs in time polynomial in the instance size (universe_size + total number
of listed elements).
"""


def reduce(instance):
    """Return a Subset Sum instance that is yes iff ``instance`` is yes."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    base = len(sets) + 1
    powers = [base ** element for element in range(universe_size)]

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)
    return {"numbers": numbers, "target": target}
