"""Reduction from Exact Cover to Subset Sum.

The reduction encodes each set as a number in a mixed‑radix system where the
radix (base) is ``u + 1`` with ``u`` the size of the universe.  For a set ``S``
its encoding is ``sum_{i in S} base**i``.  Because ``base`` is larger than the
maximum possible digit (which is 1) there is never a carry when adding the
encodings of disjoint sets.  Consequently a collection of sets forms an exact
cover iff the sum of the corresponding numbers equals the target value
``sum_{i=0}^{u-1} base**i`` – the representation of a vector of ``u`` ones.

Edge cases:
* ``u = 0`` – the empty universe.  Exact Cover is trivially a *yes* instance.
  We map it to the Subset Sum instance ``{"numbers": [], "target": 0}`` which
  is also always a *yes* (empty sub‑list sums to ``0``).
* Empty sets contribute ``0`` to the sum and never help to reach the target,
  therefore they are omitted from the list of numbers.
* Duplicate non‑empty sets are allowed in the input but can never both be
  selected in a valid exact cover; the encoding would produce a digit ``2`` in
  some position, making the total exceed the target, so the reduction remains
  correct.

The function runs in time polynomial in the size of the input (linear in the
total number of elements across all sets) and uses only integer arithmetic.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary that satisfies :class:`ExactCover`'s validation rules.

    Returns
    -------
    dict
        An instance for :class:`SubsetSum` such that the answer to the
        Subset‑Sum instance is *yes* iff the original Exact‑Cover instance is
        *yes*.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the format is wrong.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Trivial empty universe case.
    if u == 0:
        return {"numbers": [], "target": 0}

    base: int = u + 1

    # Target is the number whose base‑`base` representation consists of `u`
    # ones, i.e. sum_{i=0}^{u-1} base**i.
    target: int = sum(pow(base, i) for i in range(u))

    numbers: List[int] = []
    for s in sets:
        if not s:
            # Empty sets never affect the sum; they can be omitted.
            continue
        # Encode the set as described in the module docstring.
        num = sum(pow(base, elem) for elem in s)
        numbers.append(num)

    # Validate the produced target instance before returning.
    SubsetSum.validate({"numbers": numbers, "target": target})
    return {"numbers": numbers, "target": target}

