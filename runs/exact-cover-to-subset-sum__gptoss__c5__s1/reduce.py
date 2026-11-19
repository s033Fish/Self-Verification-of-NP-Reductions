"""Reduction from Exact Cover to Subset Sum.

The reduction follows a standard encoding using a large base.  For a universe
of size ``u`` and a collection of ``m`` sets we pick a base ``B = m + 1``.  For
each set ``S`` we create a number ``n_S = sum_{i in S} B**i``.  Because ``B`` is
strictly larger than the number of sets, the contribution of any element to a
sum of selected numbers can never reach ``B`` – therefore no carries occur when
adding the numbers in base ``B``.

The target value is the number whose representation in base ``B`` has a ``1``
in every digit corresponding to an element of the universe: ``T = sum_{i=0}^{u-1} B**i``.

Selecting a sub‑list of the numbers that sums to ``T`` is equivalent to picking
sets that are pairwise disjoint and whose union is the whole universe – i.e.
an exact cover.  Edge cases (empty universe, empty sets) are handled
automatically by the construction.

The ``reduce`` function validates the input instance using the ``ExactCover``
class and returns a dictionary that conforms to the ``SubsetSum`` instance
format.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` and ``"sets"`` as defined
        by :class:`ExactCover`.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` that is a
        yes‑instance iff the original Exact‑Cover instance is a yes‑instance.
    """
    # Validate the source instance – this will raise InvalidInstance on bad
    # input, matching the contract of the task.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    m = len(sets)
    # Base larger than the maximum possible digit sum (which is at most m).
    base = m + 1

    numbers: List[int] = []
    for s in sets:
        # Each set may be empty; its contribution is therefore 0.
        value = 0
        for elem in s:
            # elem is guaranteed to be in 0..u-1 by validation.
            value += pow(base, elem)
        numbers.append(value)

    # Target: one copy of each element (digit 1 in each position).
    target = sum(pow(base, i) for i in range(u))

    # Validate the produced target instance before returning.
    SubsetSum.validate({"numbers": numbers, "target": target})
    return {"numbers": numbers, "target": target}

