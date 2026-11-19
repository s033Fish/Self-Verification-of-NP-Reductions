"""Reduction from Subset Sum to Partition.

The source problem (SubsetSum) expects an instance of the form:
    {"numbers": [a1, a2, ...], "target": t}
where the numbers are non‑negative integers and the target may be any integer.

The target problem (Partition) expects an instance of the form:
    {"numbers": [b1, b2, ...]}
and asks whether the multiset can be split into two groups of equal sum.

We implement a classic polynomial‑time many‑one reduction.  Let
    S = sum(numbers).
If the Subset‑Sum instance is a *yes* instance, there is a sub‑list X
with sum t.  Define an extra element e = S - 2*t (which is non‑negative
whenever t ≤ S).  Consider the list B = numbers ∪ {e}.  The total sum of
+B is 2·(S - t) and half of it is S - t.  The partition
   (X ∪ {e})  vs  (complement of X)
has both sides equal to S - t, establishing a yes instance of Partition.

Conversely, any partition of B must place the extra element e on one
side; the equality of the two sides forces the numbers on the opposite
side to sum to S - t, which implies the existence of a subset of the
original numbers summing to t.

The reduction also correctly handles edge cases dictated by the problem
definitions:
* t < 0  → Subset‑Sum is always *no*; we map to a Partition instance with
  an odd total (e.g., [1]) which is always *no*.
* t = 0  → Subset‑Sum is always *yes* (empty sub‑list); we map to the empty
  list, which Partition treats as *yes*.
* t > S  → impossible to achieve, thus *no*; we map again to an odd‑total
  instance.
* For targets larger than S/2 we use the complement trick: a subset
  summing to t exists iff a subset summing to S‑t exists.  This ensures
  the extra element e is non‑negative.

The function runs in linear time with respect to the size of the input
list and uses only integer arithmetic, satisfying the polynomial‑time
requirement.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        Must contain the keys "numbers" (list of non‑negative ints) and
        "target" (int).

    Returns
    -------
    dict
        A Partition instance with a single key "numbers".
    """

    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge cases according to the Subset‑Sum definition
    if target < 0:
        # Always no → return a Partition instance that is provably no.
        return {"numbers": [1]}  # odd total sum → no partition

    if target == 0:
        # Always yes → empty list is a yes instance for Partition.
        return {"numbers": []}

    total = sum(numbers)

    if target > total:
        # Impossible to reach target → map to a known no instance.
        return {"numbers": [1]}

    # Use complement trick to ensure target ≤ total/2, guaranteeing
    # the extra element is non‑negative.
    if target > total / 2:
        target = total - target

    # Now 0 ≤ target ≤ total/2, so extra = total - 2*target is ≥ 0.
    extra = total - 2 * target
    new_numbers = numbers + [extra]
    return {"numbers": new_numbers}

