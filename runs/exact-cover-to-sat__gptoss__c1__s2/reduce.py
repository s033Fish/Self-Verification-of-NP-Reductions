"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined by an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...]}

where the universe consists of the elements ``0 .. u-1`` and each inner
list describes a set (the list may be empty and sets may be duplicated).

The target problem (Sat) expects a CNF formula represented as::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered ``1 .. m``.  A *literal* is a signed integer – a
positive integer ``v`` denotes the variable ``v`` being **true**, and a
negative integer ``-v`` denotes the variable ``v`` being **false**.  A
clause is satisfied if at least one of its literals is true; a formula is
sat‑ifiable if there exists a truth assignment satisfying every clause.

The classic polynomial‑time reduction encodes the choice of each set with a
boolean variable ``x_i`` (``i`` is 1‑based).  For every element ``e`` of the
universe we must enforce two conditions:

1. **Coverage** – at least one chosen set contains ``e``.
2. **Uniqueness** – at most one chosen set contains ``e``.

Condition 1 is expressed by a single clause containing all variables that
correspond to sets containing ``e`` (a positive literal for each).  If no
set contains ``e`` we add an empty clause ``[]`` which is unsatisfiable –
this mirrors the fact that the Exact Cover instance is a ``no`` instance.

Condition 2 is expressed by pairwise constraints: for every distinct pair
``(i, j)`` of sets that both contain ``e`` we add the clause ``[-i, -j]``
which forbids selecting both sets simultaneously.

Empty sets never appear in any of the above clauses because they contain
no elements; they are therefore unrestricted, matching the semantics of
Exact Cover where empty sets can be chosen arbitrarily.

Edge cases handled explicitly:

* ``universe_size == 0`` – the instance is trivially a ``yes``.  The
  reduction returns a SAT formula with the same number of variables but
  **no** clauses, which is satisfiable.
* ``sets`` may contain duplicates; the reduction treats each occurrence as
  a distinct variable, which is safe because the pairwise ``¬x_i ∨ ¬x_j``
  constraints will prevent selecting two identical non‑empty sets.

The function runs in time polynomial in the size of the Exact Cover
instance (``O(u * n^2)`` in the worst case, where ``n`` is the number of
sets), satisfying the required complexity bound.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"``
        (list of list of ints) describing the Exact Cover problem.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.Sat``.
    """

    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])

    num_vars = len(sets)
    clauses: List[List[int]] = []

    # If the universe is empty, the Exact Cover instance is a yes-instance.
    # A SAT formula with no clauses is always satisfiable, regardless of the
    # number of variables, so we can simply return an empty clause list.
    if u == 0:
        return {"num_vars": num_vars, "clauses": []}

    # Build a mapping from each element to the list of set indices (0‑based)
    # that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            # Guard against out‑of‑range elements; the problem statement
            # guarantees they are within 0..u-1, but we stay defensive.
            if 0 <= e < u:
                element_to_sets[e].append(idx)

    # For each element enforce coverage and uniqueness.
    for e in range(u):
        containing = element_to_sets[e]
        if not containing:
            # No set covers this element → unsatisfiable.  Encode with an
            # empty clause.
            clauses.append([])
            continue

        # Coverage: at least one of the containing sets must be chosen.
        coverage_clause = [idx + 1 for idx in containing]  # positive literals
        clauses.append(coverage_clause)

        # Uniqueness: at most one chosen set. Add pairwise negative clauses.
        n = len(containing)
        for i in range(n):
            vi = containing[i] + 1
            for j in range(i + 1, n):
                vj = containing[j] + 1
                clauses.append([-vi, -vj])

    return {"num_vars": num_vars, "clauses": clauses}

