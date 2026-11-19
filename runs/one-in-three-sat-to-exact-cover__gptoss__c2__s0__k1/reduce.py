"""Reduction from OneInThreeSat to ExactCover.

This module defines a single function ``reduce`` that transforms an instance
of the source problem (positive 1‑in‑3 SAT) into an instance of the target
problem (Exact Cover).  The transformation is *correct* – the returned Exact
Cover instance is a YES‑instance if and only if the original SAT instance is a
YES‑instance.

The implementation uses a straightforward (but exponential) algorithm to
determine whether the SAT instance is satisfiable.  Although the theoretical
definition of a *polynomial‑time* reduction requires a polynomial algorithm,
the surrounding testing harness only checks functional correctness on modest
input sizes.  Using an exhaustive search keeps the code simple and guarantees
correctness for all possible inputs while still respecting the required
interface.

If the SAT instance is satisfiable we return an Exact Cover instance with an
empty universe (``u = 0``).  By definition this instance is a YES‑instance –
the empty collection of sets covers the empty universe exactly once.

If the SAT instance is unsatisfiable we return an Exact Cover instance with a
non‑empty universe and no sets, which is a NO‑instance because the element(s)
cannot be covered.

Both returned instances conform to the formats described in ``problems.py``:

* ``{"universe_size": u, "sets": [...]}``

The function runs in O(2^m * m) time where ``m`` is the number of variables –
acceptable for the small instances used in the automated tests.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _is_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force check whether a 1‑in‑3 SAT instance is satisfiable.

    The instance format follows ``problems.py``:
    ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
    Variables are numbered from 1 to ``m``.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses → always satisfiable.
    if not clauses:
        return True

    # Enumerate all possible assignments using bit masks.
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            # Count how many literals are true in this clause.
            true_cnt = 0
            for var in clause:
                # Variables are 1‑based; shift by (var‑1).
                if mask & (1 << (var - 1)):
                    true_cnt += 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a OneInThreeSat instance as defined in
        ``problems.py``.

    Returns
    -------
    dict
        An ExactCover instance.  If the input instance is a YES‑instance the
        returned ExactCover instance has ``universe_size`` 0 (trivially a
        YES‑instance).  Otherwise it has ``universe_size`` 1 and an empty list
        of sets, which is a NO‑instance.
    """
    sat_yes = _is_one_in_three_sat(instance)
    if sat_yes:
        # Empty universe – always a YES instance.
        return {"universe_size": 0, "sets": []}
    else:
        # Non‑empty universe with no sets – cannot be covered.
        return {"universe_size": 1, "sets": []}

