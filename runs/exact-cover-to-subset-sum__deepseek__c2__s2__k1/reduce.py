"""Polynomial-time reduction from Exact Cover to Subset Sum.

Idea
----
Let ``u`` be the universe size and ``m`` the number of available sets.  Work in
base ``B = m + 1``.  Encode an element ``e`` by the digit position ``e``.

* For every set ``S`` emit the number ``n(S) = sum_{e in S} B**e``.
* The target is the number whose every digit (positions ``0..u-1``) is ``1``:
  ``t = sum_{e=0}^{u-1} B**e``.

Choosing a sub-list of the emitted numbers corresponds to choosing a
sub-collection of sets.  The digit at position ``e`` of the sum is exactly the
number of chosen sets that contain element ``e``.  Because at most ``m`` sets
are chosen, every digit lies in ``0..m < B``, so there is never a carry between
digit positions.  Hence the sum equals ``t`` iff every element is contained in
exactly one chosen set, i.e. iff the chosen sets form an exact cover.

Edge cases
----------
* ``u = 0``: the target is ``0`` (empty sum), which Subset Sum always accepts.
* Empty sets become the number ``0`` and can be added or omitted freely; they
  never change the sum, matching the fact that they never matter.
* Duplicate sets become equal numbers; taking two copies would put a ``2`` in
  some digit, so they cannot both be used (as required).
* ``m = 0`` (no sets): the base is ``1``, the target is ``u`` and the number
  list is empty, so the answer is yes iff ``u = 0``.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the Exact Cover instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    m = len(sets)
    base = m + 1

    numbers = []
    for s in sets:
        value = 0
        for e in s:
            value += base ** e
        numbers.append(value)

    target = 0
    power = 1
    for _ in range(universe_size):
        target += power
        power *= base

    return {"numbers": numbers, "target": target}
