"""Reduction from Exact Cover to SAT.

The reduction creates a Boolean variable for each set in the exact‑cover
instance.  For every element *e* of the universe we add two kinds of clauses:

* **At least one** – a clause that forces at least one of the sets containing
  *e* to be chosen.
* **At most one** – for every pair of distinct sets that both contain *e* we
  add a clause ``[-i, -j]`` (i.e. ``¬x_i ∨ ¬x_j``) to forbid choosing both.

If the universe is empty the instance is trivially a YES‑instance, and we
return an empty CNF (no variables, no clauses) which is satisfiable.

The produced CNF is exactly the classic polynomial‑time reduction from Exact
Cover to SAT, and therefore the SAT instance is satisfiable iff the original
Exact Cover instance has an exact cover.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to :class:`ExactCover`'s format.

    Returns
    -------
    dict
        A dictionary conforming to :class:`Sat`'s format.
    """
    # Validate the source instance – this will raise if malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]  # size of the universe
    sets: List[List[int]] = instance["sets"]
    n = len(sets)  # number of sets → number of variables

    # Edge case: empty universe – always YES. Return an empty formula.
    if u == 0:
        return {"num_vars": n, "clauses": []}

    # Build a mapping from element to list of set indices (1‑based for SAT).
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets, start=1):
        for e in s:
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # For each element we need at‑least‑one and at‑most‑one constraints.
    for e in range(u):
        containing = element_to_sets[e]
        # At least one: the disjunction of all variables that contain e.
        if not containing:
            # No set covers this element → unsatisfiable (empty clause).
            clauses.append([])  # empty clause is always false.
            continue
        clauses.append(containing.copy())

        # At most one: for every unordered pair, add a clause forbidding both.
        for i in range(len(containing)):
            for j in range(i + 1, len(containing)):
                clauses.append([-containing[i], -containing[j]])

    # The number of variables is the number of sets.
    return {"num_vars": n, "clauses": clauses}

