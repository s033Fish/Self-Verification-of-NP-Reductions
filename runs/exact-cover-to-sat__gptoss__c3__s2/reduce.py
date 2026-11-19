"""Reduction from Exact Cover to SAT.

The reduction is classic: for each set we introduce a Boolean variable that
indicates whether the set is chosen.  For every element of the universe we add
clauses that enforce *exactly one* of the covering sets is selected.

Implementation details
----------------------
* Variables are numbered starting from 1 as required by the SAT problem
  definition.
* For each element ``e`` we collect the indices of sets that contain ``e``.
  * If the list is empty the instance is unsatisfiable – we add an empty
    clause ``[]`` which can never be satisfied.
  * Otherwise we add a clause ``[+i for i in indices]`` to guarantee that at
    least one covering set is chosen.
  * To enforce *at most* one covering set we add pairwise negative clauses
    ``[-i, -j]`` for every unordered pair ``i, j`` in the list.
* Empty sets never appear in the element‑to‑set mapping, therefore they are
  unrestricted – they may be selected arbitrarily, which is consistent with
  the definition of Exact Cover (empty sets do not affect the cover).

The function runs in time polynomial in the size of the input instance – it
iterates over all sets and all elements, building at most ``O(u * s^2)``
clauses where ``u`` is the universe size and ``s`` the number of sets.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` and ``"sets"`` as defined
        by :class:`ExactCover`.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` where ``m`` is the
        number of sets.
    """
    # Validate the source instance – this will raise if malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    s = len(sets)

    # Build a mapping from element to the list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, cur_set in enumerate(sets):
        for e in cur_set:
            # Elements are guaranteed to be within 0..u-1 by validation.
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # For each element we enforce exactly‑one covering set.
    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element – the formula is unsatisfiable.
            clauses.append([])  # empty clause forces UNSAT
            continue
        # At least one covering set is chosen.
        clauses.append([idx + 1 for idx in covering])
        # At most one – add pairwise negative clauses.
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                clauses.append([-(covering[i] + 1), -(covering[j] + 1)])

    # The SAT instance may contain variables that never appear in any clause
    # (e.g., empty sets).  This is allowed by the problem definition.
    return {"num_vars": s, "clauses": clauses}

