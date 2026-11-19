"""Reduction from Exact Cover to SAT.

The source problem is :class:`ExactCover` defined in ``problems.py``.
The target problem is :class:`Sat`.

For each set in the exact‑cover instance we introduce a Boolean variable
``x_i`` that is true iff the i‑th set is selected.  The constraints are:

* **Cover** – for every element ``e`` of the universe there must be at least
  one selected set that contains ``e``.  This is encoded as a clause that is
  the disjunction of all variables whose corresponding set contains ``e``.

* **Disjointness** – no element may be covered by two different selected
  sets.  For each unordered pair of sets that both contain the same element
  we add the clause ``(~x_i ∨ ~x_j)``.

If the universe is empty the Exact Cover instance is trivially a *yes*
instance; we therefore output a SAT instance with ``num_vars = 0`` and no
clauses, which is also trivially satisfiable.  If the universe is non‑empty
but there are no sets, the reduction produces an empty clause for each
uncovered element, making the formula unsatisfiable – matching the source
answer.

The reduction runs in polynomial time: we inspect each set once and for each
element we may generate a quadratic number of pairwise clauses, which is
``O(|U|·|S|^2)`` – polynomial in the input size.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ExactCover`` format.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` such that the
        SAT instance is satisfiable iff the Exact Cover instance has an exact
        cover.
    """
    # Validate the source instance first – will raise InvalidInstance on bad input.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)  # number of variables

    # Edge case: empty universe – always yes.
    if u == 0:
        return {"num_vars": 0, "clauses": []}

    # Build a mapping from element to list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # 1. Cover clauses – at least one set covering each element.
    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set contains this element → unsatisfiable. Represent with empty clause.
            clauses.append([])
        else:
            # Clause is the disjunction of the positive literals of those variables.
            clauses.append([idx + 1 for idx in covering])

    # 2. Disjointness clauses – for each element, any two sets covering it cannot both be chosen.
    for e in range(u):
        lst = element_to_sets[e]
        n = len(lst)
        for i in range(n):
            for j in range(i + 1, n):
                # (~x_i ∨ ~x_j) encoded as negative literals.
                clauses.append([-(lst[i] + 1), -(lst[j] + 1)])

    # The number of variables is the number of sets. Even if some variables never appear
    # in any clause (e.g., sets that are empty), they are still allowed – SAT ignores unused vars.
    return {"num_vars": m, "clauses": clauses}
