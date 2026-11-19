"""Reduction from Exact Cover to Subset Sum.

The reduction encodes each element of the universe as a distinct digit in a
positional numeral system with base ``B = u + 1`` where ``u`` is the size of the
universe. For a set ``S`` we create a number ``n_S = sum(B**i for i in S)``.

If a collection of sets forms an exact cover, then the sum of the
corresponding numbers is ``target = sum(B**i for i in range(u))`` – each digit
appears exactly once. Conversely, any subset of the numbers that sums to the
target must use each digit at most once, because the base is larger than the
maximum possible coefficient (which would be 2 if two chosen sets shared an
element). Thus the subset corresponds to an exact cover.

The construction runs in polynomial time and uses only Python's arbitrary
precision integers, which satisfy the requirements of the Subset Sum problem.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import ExactCover, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to ``ExactCover.validate`` – it contains the
        keys ``"universe_size"`` (non‑negative int) and ``"sets"`` (list of
        lists of element indices).

    Returns
    -------
    dict
        A SubsetSum instance: ``{"numbers": [...], "target": t}``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base for the positional representation. Using u+1 guarantees that the
    # coefficient of any digit never reaches the base, preventing carries.
    base: int = u + 1

    # Encode each set as a number.
    numbers: List[int] = []
    for s in sets:
        # Empty sets contribute 0 and can be safely ignored, but we keep the
        # 0 value to preserve the one‑to‑one correspondence between input sets
        # and numbers (the SubsetSum definition allows zero values).
        value = sum(base ** i for i in s)
        numbers.append(value)

    # Target is the sum of all base powers for the whole universe.
    target: int = sum(base ** i for i in range(u))

    # Validate the produced target instance before returning.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result
