"""Reduction from Subset Sum to Partition.

The source problem (Subset Sum) instance format:
    {"numbers": [a1, a2, ...], "target": t}
The target problem (Partition) instance format:
    {"numbers": [b1, b2, ...]}

The reduction works in polynomial time and satisfies:
    SubsetSum(instance) is YES  <=>  Partition(reduce(instance)) is YES
"""
import sys
from typing import List, Dict, Any

def _yes_partition_instance() -> Dict[str, List[int]]:
    """Return a Partition instance that is trivially a YES instance.
    An empty list is a YES instance because both groups are empty.
    """
    return {"numbers": []}

def _no_partition_instance() -> Dict[str, List[int]]:
    """Return a Partition instance that is trivially a NO instance.
    The list [1, 2] has total sum 3 (odd), therefore cannot be partitioned.
    """
    return {"numbers": [1, 2]}

def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        Must contain the keys "numbers" (list of non‑negative ints) and
        "target" (int).  The format follows the definition in ``problems.py``.

    Returns
    -------
    dict
        A Partition instance (dictionary with a single key "numbers").
    """
    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge cases dictated by the Subset Sum definition.
    if target < 0:
        # Subset Sum is always NO; give a Partition instance that is also NO.
        return _no_partition_instance()
    if target == 0:
        # Subset Sum is always YES (empty subset); give a trivially YES Partition.
        return _yes_partition_instance()
    total = sum(numbers)
    if target > total:
        # Impossible to reach a larger target; Subset Sum is NO.
        return _no_partition_instance()

    # Standard polynomial‑time reduction.
    # Add two numbers: 2*target and 2*total - 2*target.
    # Both are non‑negative because 0 <= target <= total.
    extra1 = 2 * target
    extra2 = 2 * total - 2 * target
    new_numbers = list(numbers) + [extra1, extra2]
    return {"numbers": new_numbers}


if __name__ == "__main__":
    # Allow simple command‑line testing: read JSON from stdin and output JSON.
    import json
    instance = json.load(sys.stdin)
    json.dump(reduce(instance), sys.stdout)
    sys.stdout.flush()
