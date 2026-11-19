"""Reduction from Exact Cover to SAT.

The reduction creates a Boolean variable for each set in the Exact Cover
instance. For every element `e` of the universe we add clauses that enforce
*exactly one* of the sets containing `e` to be chosen:

* At‑least‑one:  (x_i1 ∨ x_i2 ∨ …) where each `i_k` is a set that contains `e`.
* At‑most‑one:  for every pair of such sets we add (¬x_i ∨ ¬x_j).

If an element is not contained in any set we add an empty clause `[]`, which
makes the CNF unsatisfiable – this matches the fact that the Exact Cover
instance is a NO‑instance.

The construction runs in time polynomial in the size of the input (the
number of sets and the size of the universe) and produces a valid SAT
instance according to the specification in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ExactCover`` specification.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the Exact Cover instance first – this will raise if malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    m = len(sets)  # number of Boolean variables
    clauses: List[List[int]] = []

    # Pre‑compute for each element the list of set indices (1‑based for SAT).
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets, start=1):
        for e in s:
            element_to_sets[e].append(idx)

    # For each element enforce exactly‑one.
    for e in range(u):
        containing = element_to_sets[e]
        if not containing:
            # No set covers this element → unsatisfiable.
            clauses.append([])  # empty clause makes the CNF unsat
            continue
        # At‑least‑one
        clauses.append(containing.copy())
        # At‑most‑one (pairwise)
        n = len(containing)
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-containing[i], -containing[j]])

    # The SAT instance may have zero variables; that is allowed.
    sat_instance: Dict[str, Any] = {"num_vars": m, "clauses": clauses}
    # Validate the produced SAT instance.
    Sat.validate(sat_instance)
    return sat_instance

