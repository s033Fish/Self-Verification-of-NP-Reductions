"""Reduction from Exact Cover to SAT.

The reduction is classic: for each set we create a Boolean variable that
indicates whether the set is chosen.  For every element of the universe we
need *exactly* one of the sets containing that element to be chosen.  In CNF
this is expressed as:

* a clause that at least one of the relevant variables is true, and
* for every pair of those variables a clause that forbids them both being
  true.

If an element is not covered by any set we generate an empty clause, which
makes the formula unsatisfiable.  The edge case ``universe_size == 0`` is a
trivial yes‑instance; we return a formula with no clauses (which is always
sat).

The function ``reduce`` validates the input, builds the CNF instance and
validates the output before returning it.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary following the ExactCover format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).  The
        instance is guaranteed to be valid according to ``Sat.validate``.
    """
    # Validate the source instance.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n = len(sets)  # number of variables

    clauses: List[List[int]] = []

    # Edge case: empty universe – always satisfiable.
    if u == 0:
        # No constraints needed; still need a valid SAT instance.
        sat_instance = {"num_vars": n, "clauses": []}
        Sat.validate(sat_instance)
        return sat_instance

    # Build a mapping from element to list of set indices (1‑based for SAT).
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets, start=1):  # SAT variables are 1‑based
        for e in s:
            element_to_sets[e].append(idx)

    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element – the formula must be unsatisfiable.
            # The simplest way is to add an empty clause.
            clauses.append([])
            continue
        # At least one set covering e must be chosen.
        clauses.append(covering[:])
        # No two sets covering e may both be chosen.
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                clauses.append([-covering[i], -covering[j]])

    sat_instance = {"num_vars": n, "clauses": clauses}
    Sat.validate(sat_instance)
    return sat_instance

