"""Polynomial-time reduction from Exact Cover to Subset Sum.

Given an Exact Cover instance ``{"universe_size": u, "sets": [...]}`` we
encode element ``e`` as the base-``B`` digit weight ``B**e``.  Choosing
``B = max(2, len(sets) + 1)`` guarantees that no carry can ever occur when
adding the numbers of several chosen sets, because at every digit position
the digit sum is at most the number of sets, which is strictly less than
``B``.

Each set is mapped to the sum of the weights of its elements, and the
target is the sum of all ``u`` weights, i.e. the number whose base-``B``
representation is ``111...1`` (``u`` ones).  A sub-list of the produced
numbers sums to the target exactly when the corresponding sets are
pairwise disjoint and cover every element of the universe.

Empty sets become the number 0 (harmless), and duplicate sets become
duplicate numbers (choosing two copies would put a digit 2 at some
position, which cannot match the all-ones target because there is no
carry).  For ``u = 0`` the target is 0 and the empty sub-list witnesses
"yes", matching the Exact Cover edge case.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    # Base larger than the number of sets so digit sums never carry.
    base = max(2, len(sets) + 1)

    # weights[e] = base ** e, for e = 0 .. universe_size - 1.
    weights = []
    power = 1
    for _ in range(universe_size):
        weights.append(power)
        power *= base

    # Target has a 1 in every base-base digit, i.e. covers each element once.
    target = sum(weights)

    numbers = []
    for group in sets:
        total = 0
        for element in group:
            total += weights[element]
        numbers.append(total)

    return {"numbers": numbers, "target": target}
