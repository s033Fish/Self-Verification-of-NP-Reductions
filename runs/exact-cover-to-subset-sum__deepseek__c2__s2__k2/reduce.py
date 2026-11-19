"""Polynomial-time reduction from Exact Cover to Subset Sum.

Construction
------------
Let the Exact Cover instance have universe size ``u`` and ``m`` sets.
Pick the base ``B = m + 1``.  For every set ``S_j`` build the integer

    a_j = sum_{e in S_j} B^e

i.e. the number whose base-B digit at position ``e`` is 1 exactly when
element ``e`` belongs to ``S_j`` (and 0 otherwise).  The target is

    t = sum_{e=0}^{u-1} B^e

whose base-B representation is a 1 in every one of the ``u`` positions.

Correctness
-----------
Every digit of every ``a_j`` is 0 or 1, so at any position the sum of the
digits of the chosen numbers is between 0 and ``m``.  Because ``B = m+1``
this sum is strictly less than the base, hence adding the chosen numbers
produces no carries and the base-B digits of the total are exactly the
per-position sums.  Therefore the total equals ``t`` iff every position
sums to exactly 1, i.e. iff the chosen sets are pairwise disjoint and
cover every element of the universe exactly once.  That is precisely an
exact cover.

Edge cases
----------
* ``u = 0``: the target is ``0`` and the empty sub-list witnesses it, so
  the answer is yes, matching Exact Cover.
* Empty sets contribute the number ``0``; they can be added or omitted
  without changing any sum, so they never matter.
* Two copies of the same non-empty set would both put a 1 in some shared
  position, giving a digit of 2 and thus a different total, so they can
  never both be used.
* ``m = 0`` gives ``B = 1``; there are no numbers and the target is
  ``u``, which is reachable only when ``u = 0`` -- exactly the Exact
  Cover answer.

The numbers have ``O(u * log m)`` bits and there are ``m`` of them, so the
construction runs in time polynomial in the input size.
"""


def reduce(instance):
    """Map an Exact Cover instance to a Subset Sum instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # Base large enough that no digit position can overflow into the next.
    base = num_sets + 1

    # powers[e] == base ** e
    powers = [1] * (universe_size + 1)
    for e in range(1, universe_size + 1):
        powers[e] = powers[e - 1] * base

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers[e] for e in range(universe_size))

    return {"numbers": numbers, "target": target}
