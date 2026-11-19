"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The classic reduction
to Subset Sum is to ask whether there exists a subset whose sum is exactly half
of the total sum.

Implementation details:
* If the total sum is even, we forward the original list of numbers and set
  the target to ``total // 2``.  In this case a Subset‑Sum solution corresponds
  exactly to a partition of the original instance.
* If the total sum is odd, the Partition instance is a definite *no*.
  To preserve correctness we return a Subset‑Sum instance that is also a
  definite *no*.  The simplest such instance is an empty list with a non‑zero
  target (e.g., ``target = 1``), because the empty list can only sum to ``0``.

The function runs in linear time with respect to the number of input numbers,
which is polynomial, satisfying the reduction requirements.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a Subset‑Sum instance.

    Args:
        instance: A dictionary with a single key ``"numbers"`` mapping to a
            list of non‑negative integers, as defined by the Partition
            problem in ``problems.py``.

    Returns:
        A dictionary representing a Subset‑Sum instance with keys
        ``"numbers"`` and ``"target"``.
    """
    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    # If the total sum is odd, Partition is a guaranteed NO.  Return an instance
    # of Subset‑Sum that is also a guaranteed NO: empty list with non‑zero target.
    if total % 2 == 1:
        return {"numbers": [], "target": 1}

    # Even total: ask for a subset that sums to half of the total.
    target = total // 2
    return {"numbers": numbers.copy(), "target": target}

