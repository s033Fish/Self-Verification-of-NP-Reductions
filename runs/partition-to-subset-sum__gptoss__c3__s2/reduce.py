"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether a multiset of non‑negative
integers can be split into two groups of equal sum.  The classic reduction
to Subset Sum is:

* Let ``S`` be the total sum of the numbers.
* If ``S`` is even, a partition exists iff there is a subset that sums to
  ``S // 2``.
* If ``S`` is odd, the answer is always ``No``.  We therefore map the
  instance to a Subset‑Sum instance that is provably unsatisfiable – any
  negative target works because Subset‑Sum defines ``t < 0`` as a guaranteed
  ``No``.

The reduction runs in polynomial time (linear in the length of the input
list) and preserves the yes‑answer exactly.
"""

from __future__ import annotations

from typing import Any, Dict

# Import the problem classes to reuse their validation helpers if needed.
from problems import SOURCE, TARGET


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A valid Partition instance – a dict with a ``"numbers"`` key
        containing a list of non‑negative integers.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` such that
        ``TARGET.is_yes`` on the returned instance yields the same boolean as
        ``SOURCE.is_yes`` on the original.
    """
    # Validate the input using the Partition class (helps catch malformed
    # instances early and mirrors the expectations of the benchmark).
    SOURCE.validate(instance)

    numbers = list(instance["numbers"])  # make a shallow copy – not strictly needed
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # Any negative target is a guaranteed "No" for Subset Sum.
        target = -1

    reduced = {"numbers": numbers, "target": target}
    # Validate the produced Subset‑Sum instance to ensure we conform to the
    # specification.
    TARGET.validate(reduced)
    return reduced

