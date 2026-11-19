"""Polynomial-time reduction from Exact Cover to Subset Sum.

Construction
------------
Let the Exact Cover instance have universe size ``u`` and ``m`` sets.

* If some universe element is in no set, the answer is no; return the
  trivially-no Subset Sum instance ``{"numbers": [], "target": 1}``.
* If ``u == 0`` the answer is yes; return ``{"numbers": [], "target": 0}``.
* Otherwise choose base ``B = m + 1``.  Every set ``S`` becomes the number
  ``sum_{e in S} B**e`` and the target is ``sum_{j=0}^{u-1} B**j``.

Because a set contains each element at most once, choosing any collection
of sets gives a digit sum of at most ``m`` in every base-``B`` position,
and ``m < B``, so there are never any carries.  A sub-list therefore sums
to the target exactly when, in every position, exactly one chosen set
contributes a 1 -- i.e. exactly when the chosen sets form an exact cover.
Empty sets contribute 0 and are harmless; two copies of a non-empty set
would give a digit 2 and cannot both be used.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    covered = 0
    for subset in sets:
        for element in subset:
            covered |= 1 << element
    full = (1 << universe_size) - 1

    # Some element is in no set: no exact cover is possible.
    if covered != full:
        return {"numbers": [], "target": 1}

    # Empty universe: the empty choice is an exact cover.
    if universe_size == 0:
        return {"numbers": [], "target": 0}

    base = len(sets) + 1
    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += base ** element
        numbers.append(value)

    target = 0
    power = 1
    for _ in range(universe_size):
        target += power
        power *= base

    return {"numbers": numbers, "target": target}
