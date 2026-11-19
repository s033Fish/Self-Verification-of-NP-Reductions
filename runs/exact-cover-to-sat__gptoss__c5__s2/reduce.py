"""Reduction from Exact Cover to SAT.

The source problem is :class:`ExactCover` (see ``problems.py``) and the
target problem is :class:`Sat`.  The reduction creates a CNF formula that is
satisfiable iff the exact‑cover instance has a solution.

For each set ``S_i`` we introduce a Boolean variable ``x_i`` which is true
iff the set is chosen in the exact cover.  For every element ``e`` of the
universe we add two kinds of constraints:

* **At least one** of the sets containing ``e`` must be chosen – a clause
  ``(x_i1 ∨ x_i2 ∨ …)``.
* **At most one** of those sets may be chosen – for every pair ``i, j``
  that both contain ``e`` we add the clause ``(¬x_i ∨ ¬x_j)``.

If an element has no covering set we produce an *empty* clause which makes
the formula unsatisfiable (SAT treats an empty clause as always false).

Edge cases:
* ``universe_size == 0`` – the exact‑cover instance is trivially a yes.
  We output a SAT instance with zero variables and zero clauses, which is
  satisfiable.
* Empty sets never appear in any clause because they contain no elements;
  they are therefore irrelevant to the formula – they may be assigned any
  value.

The construction is polynomial in the size of the input (``O(u + n + Σk_e²)``)
and runs in deterministic polynomial time.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ExactCover format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance – will raise InvalidInstance on error.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n = len(sets)  # number of variables in the SAT formula

    # Trivial yes case: empty universe – any assignment works.
    if u == 0:
        return {"num_vars": n, "clauses": []}

    clauses: List[List[int]] = []

    # Build a mapping from element to list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            element_to_sets[e].append(idx)

    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element – unsatisfiable.  An empty clause is
            # the canonical way to express falsehood in CNF.
            return {"num_vars": n, "clauses": [[]]}
        # At least one set covering e must be selected.
        at_least_one = [idx + 1 for idx in covering]  # SAT variables are 1‑based
        clauses.append(at_least_one)
        # At most one – pairwise mutual exclusion.
        for i, j in combinations(covering, 2):
            clauses.append([-(i + 1), -(j + 1)])

    # The formula may contain variables that never appear (empty sets).  This
    # is fine – SAT does not require every variable to occur.
    return {"num_vars": n, "clauses": clauses}
