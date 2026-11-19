"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined by an instance of the form::

    {"universe_size": u, "sets": [[e0, e1, ...], ...]}

where the universe consists of the elements ``0 .. u-1`` and each inner
list describes a set (the elements are distinct, the order is irrelevant).

The target problem (Sat) expects a CNF formula encoded as::

    {"num_vars": m, "clauses": [[lit, ...], ...]}

Variables are numbered ``1 .. m``.  A literal is an integer ``+v`` for the
positive literal ``v`` and ``-v`` for the negated literal ``v``.

The reduction creates a Boolean variable ``x_i`` for every set ``i`` (using
the natural 1‑based indexing of the SAT format).  The exact‑cover condition
that each element of the universe appears **exactly once** in the chosen
sets can be expressed with the following CNF constraints:

* **At least one** set containing element ``e`` is chosen:
  ``(x_i1 ∨ x_i2 ∨ …)`` where ``i1, i2, …`` are the indices of sets that
  contain ``e``.
* **At most one** set containing ``e`` is chosen:
  for every distinct pair ``(i, j)`` among those indices add
  ``(¬x_i ∨ ¬x_j)``.

If an element has *no* covering set, the original instance is a definite
"no".  In SAT we encode this by adding an empty clause ``[]`` which is
unsatisfiable.

Edge cases:
    * ``u == 0`` – the empty universe is always exactly covered (by choosing
      no sets).  We therefore return a trivially satisfiable SAT instance
      with zero variables and zero clauses.
    * Empty sets are harmless – they never contribute literals to any
      clause, so they can be ignored by the construction.

The transformation runs in time polynomial in the size of the input
(``O(u * s²)`` where ``s`` is the maximum number of sets containing a single
element) which satisfies the requirement.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"``
        (list of list of ints) as described in the problem statement.

    Returns
    -------
    dict
        A SAT instance dictionary with keys ``"num_vars"`` and ``"clauses"``.
    """

    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])

    # Trivial yes case: empty universe.
    if u == 0:
        return {"num_vars": 0, "clauses": []}

    m = len(sets)  # number of variables
    clauses: List[List[int]] = []

    # Build a mapping from element to list of set indices (1‑based).
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets, start=1):
        for e in s:
            if 0 <= e < u:
                element_to_sets[e].append(idx)
            else:
                # Elements outside the universe can be ignored – they never
                # affect the exact‑cover condition.
                continue

    # For each element, add the at‑least‑one clause and the at‑most‑one
    # pairwise clauses.
    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element ⇒ unsatisfiable. Add an empty clause.
            clauses.append([])
            continue
        # At least one covering set must be chosen.
        clauses.append(covering.copy())
        # At most one: for each pair add a clause with both literals negated.
        n = len(covering)
        for i in range(n):
            vi = covering[i]
            for j in range(i + 1, n):
                vj = covering[j]
                clauses.append([-vi, -vj])

    return {"num_vars": m, "clauses": clauses}


__all__ = ["reduce"]
