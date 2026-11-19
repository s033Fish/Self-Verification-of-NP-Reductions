"""Reduction from Exact Cover to SAT (CNF).

The source problem is :class:`ExactCover` defined in ``problems.py``. An
instance is a dictionary ``{"universe_size": u, "sets": [[...], ...]}`` where
the universe consists of the elements ``0..u-1`` and ``sets`` is a list of
subsets of that universe (the subsets may be empty and may appear more than
once).

The target problem is :class:`Sat`. An instance is a dictionary ``{"num_vars":
+m, "clauses": [[literal, ...], ...]}`` where variables are numbered ``1..m``
and a literal is a non‑zero integer ``v`` (positive for the variable, negative
for its negation). A clause is satisfied if at least one literal evaluates to
``True``; a formula is satisfiable iff all its clauses can be simultaneously
true.

We construct a CNF formula that is satisfiable exactly when the exact‑cover
instance has a solution. The standard reduction uses a Boolean variable
``x_i`` for each set ``S_i`` indicating whether the set is chosen.

Constraints
------------
* **Cover each element** – for every element ``e`` of the universe, at least one
  selected set must contain ``e``. This is encoded with a clause that is the
  disjunction of all variables whose corresponding set contains ``e``.
* **Disjointness** – no two selected sets may share an element. For each pair
  of sets ``S_i, S_j`` that both contain a common element ``e`` we add the
  clause ``(¬x_i ∨ ¬x_j)``. Adding such a clause for every pair of sets that
  intersect (and for every element they share) guarantees that at most one of
  those sets can be chosen.

If an element ``e`` is not present in any set, the instance is a definite ``no``.
We encode this by inserting an empty clause ``[]`` which is unsatisfiable in the
SAT definition.

Edge cases
~~~~~~~~~~
* ``universe_size == 0`` – the exact‑cover instance is trivially a ``yes``.
  We output a formula with zero variables and zero clauses; such a formula is
  satisfiable by definition.
* Empty sets never contribute to covering any element, therefore they are not
  referenced in any clause. They become free variables, which does not affect
  satisfiability.

The reduction runs in time polynomial in the size of the input (quadratic in
the total number of element‑set incidences), which satisfies the task
requirement.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse their validation helpers if desired.
from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ExactCover specification.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable iff the original Exact Cover instance is a yes‑instance.
    """

    # Validate the input (will raise InvalidInstance if malformed).
    ExactCover.validate(instance)

    universe_size: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Number of variables equals number of sets.
    num_vars = len(sets)
    clauses: List[List[int]] = []

    # Edge case: empty universe – trivially satisfiable.
    if universe_size == 0:
        # No constraints needed; a formula with 0 clauses is always satisfiable.
        return {"num_vars": num_vars, "clauses": []}

    # Pre‑compute, for each element, the list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(universe_size)]
    for idx, s in enumerate(sets):
        for e in s:
            # The instance validation guarantees 0 <= e < universe_size.
            element_to_sets[e].append(idx)

    # Build clauses for each element.
    for e in range(universe_size):
        containing = element_to_sets[e]
        if not containing:
            # No set covers this element → unsatisfiable. Add an empty clause.
            clauses.append([])
            continue

        # At least one set covering e must be chosen.
        clauses.append([idx + 1 for idx in containing])

        # At most one: for every unordered pair add (¬x_i ∨ ¬x_j).
        for i in range(len(containing)):
            for j in range(i + 1, len(containing)):
                clauses.append([-(containing[i] + 1), -(containing[j] + 1)])

    # Validate the produced SAT instance (optional, helps catch bugs).
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

