"""Reduction from Subset Sum to Partition.

The source problem ``SubsetSum`` is defined in ``problems.py``.  An instance
has the form ``{"numbers": [...], "target": t}`` where the numbers are
non‑negative integers and ``t`` may be any integer.

The target problem ``Partition`` asks whether the multiset of numbers can be
split into two groups with equal sum.

We implement a classic polynomial‑time many‑one reduction:

* If ``t < 0`` the Subset‑Sum instance is a definite **NO** (by definition).
  We therefore return a Partition instance whose answer is also **NO** – any
  instance with an odd total sum works, e.g. ``[1]``.

* If ``t == 0`` the Subset‑Sum instance is a definite **YES** (empty subset).
  The Partition instance ``[]`` (empty list) is also a **YES**.

* For ``t > 0`` let ``S = sum(numbers)``.  We construct a new list
  ``numbers' = numbers + [S, 2*t]``.

  The total sum of ``numbers'`` is ``2*S + 2*t = 2*(S + t)`` which is even,
  so a valid partition must have each side sum ``S + t``.

  *If* there is a subset of the original numbers that sums to ``t`` (call it
  ``X``), then placing the element ``S`` together with ``X`` on one side gives
  ``S + t``.  The other side receives the element ``2*t`` and the remaining
  original numbers (which sum to ``S - t``), also totalling ``2*t + (S - t) =
  S + t``.

  Conversely, any partition of the constructed instance must place the large
  element ``S`` on one side – without it the maximum sum achievable from the
  other elements is ``S + 2*t`` which is strictly larger than the required
  half‑sum ``S + t`` unless a subset of the original numbers sums to exactly
  ``t``.  A straightforward case analysis shows that a valid partition exists
  iff the original Subset‑Sum instance is a **YES**.

Both added numbers are non‑negative because ``S`` is a sum of non‑negative
integers and ``t > 0`` ensures ``2*t`` is non‑negative.

The function validates the source instance using ``SubsetSum.validate`` and
returns a dictionary that conforms to the ``Partition`` format.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Subset‑Sum instance.

    Returns
    -------
    dict
        A dictionary representing a Partition instance whose answer matches
        that of the input instance.
    """
    # Validate the source instance first – will raise InvalidInstance on error.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])
    target: int = int(instance["target"])

    # Edge cases where the answer is known without computation.
    if target < 0:
        # No instance – return a Partition instance that is definitely NO.
        # An odd total sum guarantees a NO answer.
        return {"numbers": [1]}
    if target == 0:
        # Always YES – empty list is a YES for Partition.
        return {"numbers": []}

    # General case: target > 0.
    total = sum(numbers)
    # Construct the new list as described in the module docstring.
    new_numbers = numbers + [total, 2 * target]
    # Validate the constructed instance before returning.
    Partition.validate({"numbers": new_numbers})
    return {"numbers": new_numbers}

