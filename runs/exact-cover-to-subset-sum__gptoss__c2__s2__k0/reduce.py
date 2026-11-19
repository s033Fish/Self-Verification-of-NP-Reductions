"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...]}

where the universe consists of the elements ``0`` through ``u-1``.  The
question is whether we can pick a sub‑collection of the given sets that are
pairwise disjoint and whose union is the whole universe.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

and asks whether a sub‑list of ``numbers`` sums exactly to ``t``.

We implement the classic polynomial‑time many‑one reduction that encodes each
set as a number in a mixed‑radix (base‑B) representation.  Choose a base ``B``
that is strictly larger than the number of sets; then the digit at position
``i`` (corresponding to universe element ``i``) is either ``0`` (the element
is not in the set) or ``1`` (the element is in the set).  Because ``B`` is
larger than the total number of sets, the sum of any collection of such
numbers cannot cause a carry: each digit of the sum is at most the number of
selected sets, which is < ``B``.

Consequences:
* Selecting a collection of sets that are pairwise disjoint and cover the
  entire universe yields a digit ``1`` in every position ``0 … u‑1`` and
  therefore the sum equals ``target = Σ_{i=0}^{u-1} B**i``.
* If the chosen sets overlap, some digit would be ``≥ 2``; because no carry
  occurs, the resulting sum cannot equal the target.
* Empty sets correspond to the number ``0``; they are irrelevant for the
  decision and can safely be ignored (or kept) – subset‑sum may simply omit
  them.

The reduction runs in polynomial time: we compute ``B = m + 1`` where ``m``
is the number of input sets, and for each set we evaluate a sum of at most
``u`` powers ``B**i``.  The size of each produced integer is ``O(u·log B)``
bits, which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list
        of list of ints) describing the Exact Cover problem.

    Returns
    -------
    dict
        A Subset Sum instance with keys ``"numbers"`` (list of non‑negative
        integers) and ``"target"`` (int).
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base B must be larger than the number of sets to avoid carries.
    # Adding one also handles the case of zero sets (B = 1).
    B: int = len(sets) + 1

    # Pre‑compute powers B**i for i in 0..u-1 to reuse them.
    powers: List[int] = [pow(B, i) for i in range(u)]

    numbers: List[int] = []
    for s in sets:
        val = 0
        for elem in s:
            if 0 <= elem < u:
                val += powers[elem]
        numbers.append(val)

    # Target is the sum of all B**i for i = 0 .. u-1, i.e., the representation
    # with digit 1 in every position.
    target: int = sum(powers)

    return {"numbers": numbers, "target": target}

