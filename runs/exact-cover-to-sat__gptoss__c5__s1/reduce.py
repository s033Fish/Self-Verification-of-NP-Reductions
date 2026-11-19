"""Reduction from Exact Cover to SAT.

The reduction creates a Boolean variable for each set in the Exact Cover
instance. For every element of the universe we add clauses that enforce
*exactly* one of the sets containing that element is chosen. This is done by
adding a clause that requires *at least* one of the relevant variables to be
true and a set of pairwise clauses that forbid two of them from being true at
the same time (the standard "at‑most‑one" encoding).

If an element is not contained in any set we add an empty clause, which makes
the CNF formula unsatisfiable – this matches the fact that the Exact Cover
instance is a NO‑instance.

The implementation follows the instance formats defined in ``problems.py``
and runs in time polynomial in the size of the Exact Cover instance (the
number of sets and the total size of all sets).
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to ``ExactCover.validate``.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance first – this also guarantees the required
    # keys and that all elements are within the proper range.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)  # one Boolean variable per set, indexed 1..m in the SAT format

    # Build a mapping from each element to the list of set indices (1‑based) that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, subset in enumerate(sets, start=1):
        for e in subset:
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # For each element we need "exactly one" constraint.
    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element -> unsatisfiable. Add an empty clause.
            clauses.append([])
            continue
        # At least one covering set must be chosen.
        clauses.append(covering[:])  # positive literals
        # At most one: for each pair add a clause (-i OR -j)
        for i in range(len(covering)):
            vi = covering[i]
            for j in range(i + 1, len(covering)):
                vj = covering[j]
                clauses.append([-vi, -vj])

    sat_instance = {"num_vars": m, "clauses": clauses}
    # Validate the produced SAT instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

