"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) instance format::

    {"universe_size": u, "sets": [[element, ...], ...]}

The target problem (Sat) instance format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

We create a Boolean variable ``x_i`` for each set ``i`` (1‑based indexing as
required by the SAT format).  For every element ``e`` in the universe we add
constraints that enforce *exactly one* of the sets containing ``e`` is chosen:

* At least one – a clause containing all positive literals of those sets.
* At most one – for each pair of sets that both contain ``e`` we add a clause
  ``(-x_i ∨ -x_j)``.

If an element is not contained in any set we add an empty clause (``[]``),
which makes the formula unsatisfiable – this matches the fact that the exact
cover instance is a NO instance.

The construction runs in polynomial time in the size of the input (the
number of sets and the total size of all sets).  Empty sets do not contribute
any constraints, which is correct because they can be freely chosen without
affecting the exact‑cover condition.

Edge cases handled:
* ``universe_size == 0`` – the empty exact‑cover is always a YES instance.
  We return a SAT instance with ``0`` variables and no clauses, which is
  trivially satisfiable.
* Duplicate non‑empty sets – the pairwise ``(-x_i ∨ -x_j)`` clauses prevent
  both from being selected, exactly as required.

The module defines a single function ``reduce(instance)`` as required by the
task specification.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce an ExactCover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list of
        list of ints).  The format follows the docstring of the ``ExactCover``
        class in ``problems.py``.

    Returns
    -------
    dict
        A SAT instance respecting the format required by the ``Sat`` class:
        ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    """

    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)  # number of variables

    # Edge case: empty universe – always yes. Return a trivially satisfiable
    # formula (no variables, no clauses).
    if u == 0:
        return {"num_vars": 0, "clauses": []}

    # Build a mapping from element to the list of set indices (0‑based) that
    # contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            # ``e`` is guaranteed to be in 0..u-1 by the problem definition.
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    for e in range(u):
        containing = element_to_sets[e]
        if not containing:
            # No set covers this element -> unsatisfiable. An empty clause
            # forces the formula to be false.
            clauses.append([])
            continue

        # At least one set covering e must be chosen.
        at_least_one = [idx + 1 for idx in containing]  # SAT uses 1‑based vars
        clauses.append(at_least_one)

        # At most one: for each pair, add a clause forbidding both true.
        for i, j in combinations(containing, 2):
            clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": m, "clauses": clauses}

