"""Polynomial-time reduction from Exact Cover to Subset Sum.

Given an Exact Cover instance with universe size u and a list of m sets,
choose base b = m + 1.  Map each set S to the integer

    a_S = sum_{e in S} b^e

and map the universe to the target

    t = sum_{e=0}^{u-1} b^e.

Every element digit of t is 1.  If a sub-list of the a_S sums to t, then
writing c_e for the number of chosen sets that contain element e gives

    sum_e c_e * b^e = sum_e 1 * b^e.

Each c_e is at most the number of chosen sets, which is at most m < b.
Reducing the equation modulo b yields c_0 = 1; subtracting and dividing by
b and repeating gives c_e = 1 for every e.  Hence the chosen sets are
pairwise disjoint and cover the whole universe, i.e. they form an exact
cover.  Conversely, an exact cover clearly sums to t.

Empty sets become the number 0 and are harmless.  If m = 0, then b = 1
and the target is u (with no numbers), which is correct because an exact
cover of a non-empty universe is impossible and t = 0 is yes for u = 0.
"""


def reduce(instance):
    """Return a Subset Sum instance that is yes iff the Exact Cover input is."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    base = num_sets + 1

    # powers[e] = base ** e, for e = 0 .. universe_size - 1
    powers = [1] * universe_size
    for e in range(1, universe_size):
        powers[e] = powers[e - 1] * base

    numbers = []
    for chosen_set in sets:
        value = 0
        for element in chosen_set:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)  # 0 when universe_size == 0

    return {"numbers": numbers, "target": target}
