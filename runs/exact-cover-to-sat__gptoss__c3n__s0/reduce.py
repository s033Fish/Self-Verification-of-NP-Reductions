"""Reduction from Exact Cover to SAT.

The source problem is :class:`ExactCover` (see ``problems.py``) and the
target problem is :class:`Sat`.  The reduction creates a Boolean variable for
each set and adds clauses that enforce that each element of the universe is
covered by **exactly one** selected set.

For every element ``e`` we add:

* **At‑least‑one** clause – the disjunction of all variables whose set
  contains ``e``.  If no set contains ``e`` the formula becomes unsatisfiable
  (the clause is omitted and later the SAT solver will correctly report ``no``).
* **At‑most‑one** clauses – for every pair of distinct sets ``i`` and ``j``
  that both contain ``e`` we add the clause ``[-i-1, -j-1]`` (using the SAT
  literal encoding where a positive integer ``v`` denotes the variable ``v``
  being true and a negative integer ``-v`` denotes it being false).

The construction runs in polynomial time in the size of the exact‑cover
instance (``O(|U|·|S|^2)`` in the worst case, which is acceptable for a
polynomial‑time reduction).

The module also provides a tiny ``__all__`` list so that only ``reduce`` is
exported when using ``from reduce import *``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat

__all__ = ["reduce"]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format described in ``ExactCover``.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).  The
        returned instance is guaranteed to be valid according to
        ``Sat.validate``.
    """
    # Validate the source instance first – this will raise ``InvalidInstance``
    # if the input is malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)  # one Boolean variable per set

    # Build a mapping from element to the list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # Edge case: empty universe – the exact‑cover problem is trivially yes.
    # The corresponding SAT formula with no clauses is satisfiable, so we can
    # simply return a formula with zero variables and an empty clause list.
    if u == 0:
        return {"num_vars": 0, "clauses": []}

    # For each element, add the at‑least‑one clause and the at‑most‑one
    # pairwise clauses.
    for e in range(u):
        covering = element_to_sets[e]
        # If no set covers this element, the exact‑cover instance is a "no"
        # instance.  Adding an empty clause makes the SAT instance unsatisfiable.
        if not covering:
            clauses.append([])  # empty clause -> unsatisfiable
            continue

        # At‑least‑one: positive literals for each covering set.
        at_least_one = [idx + 1 for idx in covering]
        clauses.append(at_least_one)

        # At‑most‑one: for every unordered pair add a clause (-i OR -j).
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                vi = covering[i] + 1
                vj = covering[j] + 1
                clauses.append([-vi, -vj])

    # The constructed instance respects the SAT format.
    sat_instance = {"num_vars": m, "clauses": clauses}
    # Validate the target instance to catch programming errors early.
    Sat.validate(sat_instance)
    return sat_instance

