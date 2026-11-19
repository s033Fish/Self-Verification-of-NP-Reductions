"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) is defined by a universe of size ``u`` and a
list of subsets of that universe.  The question is whether we can select a
sub‑collection of those subsets that are pairwise disjoint and whose union is
the entire universe.

We reduce this to Subset Sum using a classic base‑encoding trick.  Let
``B = u + 1``.  For each element ``i`` of the universe we associate the weight
``B**i``.  For a set ``S`` we create a number ``n_S = Σ_{i in S} B**i``.  Because
``B`` is larger than the maximum possible digit (which is 1), adding such
numbers never creates a carry *as long as the chosen sets are disjoint*.

The target for the Subset Sum instance is the number that has a ``1`` in every
digit position, i.e. ``target = Σ_{i=0}^{u-1} B**i``.  A collection of sets forms
an exact cover iff the corresponding numbers sum to exactly this target.

The construction runs in polynomial time (linear in the total size of the
input) and handles all edge cases described in ``problems.py``:

* ``u = 0`` → ``target = 0`` and the Subset Sum instance is trivially a yes.
* Empty sets map to the number ``0`` and can be ignored by the Subset Sum
  solver.
* Duplicate non‑empty sets become duplicate numbers; picking both would cause
  a digit sum of ``2`` and therefore a carry, which cannot match the target.

The module provides a single ``reduce`` function as required by the testing
framework.
"""

from typing import List, Dict, Any


def _encode_set(s: List[int], base: int) -> int:
    """Encode a single set as an integer in the given base.

    ``s`` is a list of distinct element indices (0‑based).  ``base`` is ``u+1``.
    The returned integer has a ``1`` in the ``i``‑th digit (base ``base``) for
    each element ``i`` present in ``s``.
    """
    value = 0
    for i in s:
        # Each element contributes base**i.
        value += pow(base, i)
    return value


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list of
        list of ints) as described in ``problems.py``.

    Returns
    -------
    dict
        A SubsetSum instance with keys ``"numbers"`` (list of non‑negative
        integers) and ``"target"`` (int).
    """
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base for encoding – one larger than the universe size guarantees no
    # carries when adding numbers that correspond to disjoint sets.
    base = u + 1

    # Encode each set as a number.
    numbers: List[int] = [_encode_set(s, base) for s in sets]

    # Target is the number with a 1 in every digit position 0..u-1.
    target: int = sum(pow(base, i) for i in range(u))

    return {"numbers": numbers, "target": target}

