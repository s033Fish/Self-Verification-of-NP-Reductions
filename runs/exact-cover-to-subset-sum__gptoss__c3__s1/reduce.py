"""Reduction from Exact Cover to Subset Sum.

The source problem is ``ExactCover`` (see ``problems.py``) and the target
problem is ``SubsetSum``.  An instance of Exact Cover consists of a universe
size ``u`` and a list of sets (each set is a list of distinct elements in the
range ``0..u-1``).  The task is to decide whether a sub‑collection of the sets
covers every element exactly once.

We encode each element ``i`` of the universe as a block of bits that is
wide enough to hold the maximum possible count of that element in any chosen
sub‑collection.  If the block is wide enough, adding the numbers corresponding
to a collection of sets never produces a carry into the next block.  Hence a
subset of numbers sums to the target iff each block sums to exactly one copy
of its weight – i.e. each element appears exactly once.

Construction
------------
* Let ``m`` be the number of sets.  The maximum number of times an element can
  be added is ``m`` (if we (incorrectly) selected all sets containing it).
* Choose a shift ``s`` = ``(m + 1).bit_length()``.  Then ``2**s`` is larger
  than any possible sum within a single block.
* For element ``i`` define ``weight_i = 1 << (i * s)``.
* For each set ``S`` create a number ``n_S = sum(weight_i for i in S)``.
* The target is ``T = sum(weight_i for i in range(u))``.

If ``u == 0`` we return the trivial instance ``{"numbers": [], "target": 0}``
which is a yes‑instance for Subset Sum and matches the Exact Cover edge case.

The reduction runs in time polynomial in the size of the Exact Cover input –
only linear work plus a few integer‑bit operations.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse validation / utilities if needed.
from problems import ExactCover, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list
        of list of ints) as defined by ``ExactCover``.

    Returns
    -------
    dict
        An instance of ``SubsetSum`` – a dict with keys ``"numbers"`` and
        ``"target"`` – such that the Subset Sum answer is *yes* exactly when
        the Exact Cover answer is *yes*.
    """
    # Validate the source instance – will raise InvalidInstance on malformed
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Trivial edge case: empty universe → target 0, no numbers needed.
    if u == 0:
        return {"numbers": [], "target": 0}

    m = len(sets)
    # Shift size: enough bits to represent up to m (inclusive) without carry.
    shift = (m + 1).bit_length()
    # Pre‑compute the weight for each element.
    weights = [1 << (i * shift) for i in range(u)]

    numbers: List[int] = []
    for s in sets:
        # Empty sets contribute nothing and never affect the answer, but they
        # are allowed in the input.  We can safely skip them.
        if not s:
            continue
        num = 0
        for elem in s:
            # Elements are guaranteed to be in 0..u-1 by validation.
            num += weights[elem]
        numbers.append(num)

    target = sum(weights)
    # Return a valid SubsetSum instance.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)  # ensure we produced a correct instance
    return result

