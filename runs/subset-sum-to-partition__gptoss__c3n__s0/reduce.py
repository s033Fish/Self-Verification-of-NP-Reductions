"""Reduction from Subset Sum to Partition.

The source problem is defined in :class:`problems.SubsetSum` and expects an
instance of the form `{"numbers": [...], "target": t}`.  The target problem
is :class:`problems.Partition` with an instance `{"numbers": [...]}`.

The reduction is classic: given a multiset ``A`` with total sum ``S`` and a
target ``t`` (non‑negative), we construct a new multiset ``B = A ∪ {y}`` where

``y = S - 2*t`` (after possibly replacing ``t`` with ``S - t`` so that ``t`` is
at most ``S/2``).  ``y`` is guaranteed to be non‑negative.  The total sum of ``B``
is ``2*(S - t)`` and a partition of ``B`` exists iff a subset of ``A`` sums to
``t``.

Edge‑case handling:
* ``t == 0`` – the empty subset always works, so we return the empty list
  (which is a yes‑instance of Partition).
* ``t < 0`` or ``t > S`` – the Subset‑Sum instance is a definite *no*; we
  return a Partition instance with an odd total (e.g. ``[1]``) which is also a
  *no*.
* Empty ``numbers`` list – covered by the cases above.

The function runs in linear time with respect to the size of the input list.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the validation classes to ensure we raise the same errors as the
# original framework when malformed instances are supplied.
from problems import SubsetSum, Partition


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the SubsetSum format.

    Returns
    -------
    dict
        A dictionary adhering to the Partition format.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is wrong, matching the behaviour of the original problem class.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])  # make a shallow copy
    t: int = instance["target"]

    # Edge cases that are independent of the actual numbers.
    if t == 0:
        # Empty subset always works – return the trivial yes‑instance for
        # Partition.
        return {"numbers": []}
    if t < 0:
        # Subset‑Sum is a definite no; produce a Partition instance that is
        # also a definite no (odd total).
        return {"numbers": [1]}

    total = sum(numbers)

    # If the list is empty we have already handled t == 0; any other t is > 0
    # and therefore a no‑instance.
    if not numbers:
        return {"numbers": [1]}

    # If the target exceeds the total sum, the answer is certainly no.
    if t > total:
        return {"numbers": [1]}

    # At this point 0 < t <= total.
    # Use the complement if it gives a smaller (or equal) target; this ensures
    # that the constructed ``y`` is non‑negative because then ``t <= total/2``.
    if t > total - t:
        t = total - t

    # Now ``t`` is at most ``total/2`` and ``y = total - 2*t`` is guaranteed to be
    # >= 0.
    y = total - 2 * t
    new_numbers = numbers + [y]

    # Validate the resulting Partition instance before returning.
    Partition.validate({"numbers": new_numbers})
    return {"numbers": new_numbers}

