"""Reduction from Exact Cover to Subset Sum.

The reduction encodes each set as a number in a mixed‑radix representation.
For an Exact Cover instance with universe size ``u`` and a list ``sets`` of
``m`` subsets, we choose a base ``B = m + 1`` (any integer larger than the
maximum number of sets that could be selected works; ``m+1`` guarantees that
the sum of the coefficients for each element never reaches ``B`` and thus no
carry occurs when numbers are added).

For a set ``S`` we create the number

    n_S = sum(B**e for e in S)

where ``e`` is an element of the universe (0‑based). The target number is the
sum of ``B**e`` for all universe elements, i.e. the representation that has a
coefficient of ``1`` for every element:

    target = sum(B**e for e in range(u))

Selecting a collection of sets corresponds to selecting the corresponding
numbers. Because the base is larger than the number of sets, the digit for a
given element in the summed number equals the number of chosen sets that
contain that element. The sum equals the target exactly when each digit is
``1`` – i.e. each element appears exactly once and the chosen sets are pair‑
wise disjoint, which is precisely an exact cover.

Edge cases:
* ``u = 0`` ⇒ target = 0. Subset‑Sum with target 0 is always a YES instance.
* The list of sets may be empty. In that case ``B = 1``; the numbers are all
  zero and the target is ``0`` when ``u = 0`` and ``u`` otherwise. The reduction
  correctly reflects that an exact cover exists only when ``u = 0``.

The function validates the source instance using ``ExactCover.validate`` and
returns a dictionary suitable for ``SubsetSum``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ExactCover format.

    Returns
    -------
    dict
        A SubsetSum instance ``{"numbers": [...], "target": t}`` that is a
        YES instance iff the input ExactCover instance is a YES instance.
    """
    # Validate the source instance – will raise InvalidInstance on bad input.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    m = len(sets)
    # Choose base larger than the maximum possible coefficient for any element.
    # Using m+1 guarantees that even if all sets contain the same element, the
    # sum of coefficients is at most m, which is < base.
    base = m + 1 if m + 1 > 1 else 1  # base = 1 only when there are no sets.

    numbers: List[int] = []
    for s in sets:
        # Encode the set as a number in base ``base``.
        num = 0
        for e in s:
            num += base ** e
        numbers.append(num)

    # Target is the number that has a coefficient 1 for every element of the
    # universe.
    target = sum(base ** e for e in range(u))

    # Validate the produced target instance before returning.
    SubsetSum.validate({"numbers": numbers, "target": target})
    return {"numbers": numbers, "target": target}

