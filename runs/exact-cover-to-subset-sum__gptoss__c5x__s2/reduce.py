"""Reduction from Exact Cover to Subset Sum.

The reduction follows the classic encoding using a large base.  For a
universe of size ``u`` we pick a base ``B`` larger than the number of sets.
Each set ``S`` is encoded as the integer ``sum_{e in S} B**e``.  The target is
``sum_{e=0}^{u-1} B**e`` – the base‑B representation consisting of a single ``1``
in every digit position.

Because ``B`` is larger than the maximum possible coefficient (which is the
total number of sets), adding the encoded numbers never produces a carry.
Consequently a subset of the numbers sums to the target **iff** the chosen
sets are pairwise disjoint and cover every element exactly once, i.e. they
form an exact cover.

The ``reduce`` function validates the Exact Cover instance, builds the list
of numbers and the target, and returns a dictionary suitable for the
``SubsetSum`` problem definition.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary matching the ``ExactCover`` specification.

    Returns
    -------
    dict
        An instance of ``SubsetSum`` – ``{"numbers": [...], "target": t}``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Choose a base larger than the number of sets to avoid carries.
    # Adding 1 ensures the base is at least 1 even when there are no sets.
    base: int = len(sets) + 1
    if base <= 1:
        # When there are no sets we can safely use base = 2 (any >1 works).
        base = 2

    numbers: List[int] = []
    for s in sets:
        # Encode the set as a sum of base powers.
        value = 0
        for e in s:
            value += base ** e
        numbers.append(value)

    # Target: one copy of each element of the universe.
    target = sum(base ** e for e in range(u))

    # Construct the SubsetSum instance and validate it for good measure.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

