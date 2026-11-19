"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) is defined by an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...]}

where the universe consists of the elements ``0 .. u-1``.  We must decide
whether there exists a sub‑collection of the given sets that partitions the
universe – i.e. the chosen sets are pairwise disjoint and their union is the
whole universe.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

with non‑negative integer ``numbers`` and an integer ``target``.  The answer is
``yes`` iff some sub‑list of ``numbers`` sums exactly to ``t``.

We implement a classic polynomial‑time reduction using a large base ``B``.
For each element ``e`` of the universe we assign the weight ``B**e``.  For a
set ``S`` we create the number ``sum(B**e for e in S)``.  The target is the sum
of all element weights, i.e. ``sum(B**e for e in range(u))``.

Choosing a collection of sets yields a sum that, when expressed in base ``B``,
has a digit equal to the number of times each element appears in the chosen
sets.  If the collection forms an exact cover, each digit is exactly ``1`` and
the total sum equals the target.  Conversely, if the sum equals the target, the
base‑``B`` representation must have digit ``1`` for every element, which means
the chosen sets are pairwise disjoint and cover the whole universe.

To avoid carries we pick ``B`` larger than both the universe size ``u`` and the
number of sets ``m``.  Setting ``B = max(u, m) + 1`` guarantees that any digit
in the sum is strictly less than ``B`` (the maximum possible digit is the
number of sets containing a particular element, which is at most ``m``).

The reduction runs in time polynomial in the size of the input (it merely
computes a few exponentiations and sums).  Edge cases are handled naturally:

* ``u == 0`` → target ``0`` and an empty list of numbers.  Subset‑Sum with
  target ``0`` is always a yes‑instance, matching the Exact‑Cover definition.
* Empty sets contribute the number ``0``; they do not affect correctness.
* Duplicate sets produce identical numbers; selecting both would create a
  digit ``2`` in the corresponding positions, which cannot equal the target
  because ``B > 2``.

The function ``reduce`` below follows the contract required by the evaluation
framework.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list
        of list of ints) representing the ExactCover problem.

    Returns
    -------
    dict
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int) representing the SubsetSum instance.
    """

    u: int = int(instance.get("universe_size", 0))
    sets: List[List[int]] = instance.get("sets", [])

    # Number of sets – used to choose a safe base.
    m: int = len(sets)

    # Choose a base larger than both the universe size and the number of sets.
    # Adding 1 ensures the base is at least 1 and avoids a base of 0.
    B: int = max(u, m) + 1

    # Pre‑compute powers of B up to u‑1 to avoid repeated exponentiation.
    # For u == 0 the list is empty.
    powers: List[int] = [pow(B, e) for e in range(u)]

    numbers: List[int] = []
    for s in sets:
        # Sum the weights for the elements present in the set.
        total = 0
        for e in s:
            # Guard against malformed elements (outside the universe).
            # The validation of the source instance is handled elsewhere, but
            # we silently ignore out‑of‑range elements to keep the reduction
            # total‑function.
            if 0 <= e < u:
                total += powers[e]
        numbers.append(total)

    # Target is the sum of all element weights.
    target = sum(powers)

    return {"numbers": numbers, "target": target}

