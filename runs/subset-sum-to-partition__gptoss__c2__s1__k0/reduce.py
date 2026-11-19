"""Reduction from Subset Sum to Partition.

The source problem (Subset Sum) instance format is:
    {"numbers": [a1, a2, ...], "target": t}
where ``numbers`` are non‑negative integers and ``target`` is any integer.

The target problem (Partition) instance format is:
    {"numbers": [b1, b2, ...]}
where the list contains non‑negative integers.

We implement a polynomial‑time many‑one reduction that preserves the answer.

Idea
----
For a Subset‑Sum instance with list ``A`` and target ``t`` let ``S = sum(A)``.
If ``t < 0`` or ``t > S`` the Subset‑Sum answer is always *no* (the target
cannot be reached).  In that case we output a trivially unsatisfiable Partition
instance – a single odd number – which is also always *no*.

Otherwise ``0 ≤ t ≤ S``.  We construct a Partition instance as follows:

* Scale every original number by two: ``A' = [2·a for a in A]``.
* Append two extra numbers ``e1 = 2·t`` and ``e2 = 2·(S‑t)``.

The total sum of the new multiset is ``2·S + 2·t + 2·(S‑t) = 4·S`` which is even,
so the Partition question asks whether there is a subset with sum ``2·S``.

Observe that a valid partition must place exactly one of ``e1`` or ``e2`` on a
side (otherwise the side containing both would already exceed ``2·S``).  If
``e1`` is on the left side, the remaining numbers on that side must sum to
``2·S - 2·t = e2``; equivalently the complement of that subset from ``A'`` sums to
``2·t``.  Thus a partition exists iff there is a subset of ``A'`` whose sum is
``2·t`` – which holds exactly when the original numbers have a subset summing
to ``t`` (scaling by two preserves subset‑sum feasibility).

Both extra numbers are non‑negative because ``0 ≤ t ≤ S``.  The construction
is clearly polynomial in the size of the input.

The function ``reduce`` implements this transformation.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        ``{"numbers": [...], "target": t}`` as defined by ``SubsetSum``.

    Returns
    -------
    dict
        ``{"numbers": [...]}`` suitable for the ``Partition`` problem.
    """
    numbers: List[int] = instance["numbers"]
    t: int = instance["target"]

    total = sum(numbers)

    # Edge cases where Subset‑Sum is definitively NO.
    if t < 0 or t > total:
        # Partition instance with an odd total is always NO.
        return {"numbers": [1]}

    # Scale original numbers by 2 to avoid fractions.
    new_numbers = [2 * x for x in numbers]
    # Append the two extra numbers described in the proof above.
    new_numbers.append(2 * t)
    new_numbers.append(2 * (total - t))

    return {"numbers": new_numbers}

