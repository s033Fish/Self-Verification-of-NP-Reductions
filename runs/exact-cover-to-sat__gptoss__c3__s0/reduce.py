"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined in ``problems.py``.  An instance is a
dictionary with keys ``"universe_size"`` (an integer ``u``) and ``"sets"`` – a
list of sets, each represented as a list of distinct elements from ``0`` to
``u-1``.  The question is whether we can pick a sub‑collection of the given
sets such that every element of the universe appears in exactly one chosen set.

The target problem (Sat) expects a CNF formula: ``{"num_vars": m,
"clauses": [[literal, ...], ...]}`` where variables are numbered ``1..m`` and a
literal is a signed integer (positive for the variable, negative for its
negation).  The formula is satisfiable iff there exists an assignment making at
least one literal true in each clause.

We encode the exact‑cover constraints in a straightforward way.  For each set
``S_i`` we introduce a Boolean variable ``x_i`` (``i`` is 1‑based).  The
constraints are:

* **Coverage** – for every element ``e`` of the universe, at least one chosen
  set must contain ``e``.  This becomes a clause ``(x_i1 ∨ x_i2 ∨ ...)`` where
  the ``i``'s are the indices of sets that contain ``e``.
* **Uniqueness** – an element may appear in at most one chosen set.  For every
  pair of distinct sets ``i`` and ``j`` that both contain ``e`` we add a clause
  ``(¬x_i ∨ ¬x_j)``.

If an element is not present in any set, the coverage clause would be empty –
an empty clause is unsatisfiable, correctly reflecting that the exact‑cover
instance is a ``no`` instance.

Edge cases:
* ``u = 0`` (empty universe) is always a ``yes`` instance.  We return a SAT
  formula with no clauses (which is trivially satisfiable) and any number of
  variables (the number of sets, possibly zero).
* Empty sets never affect the constraints because they contain no elements; the
  encoding simply ignores them.
* Duplicate non‑empty sets are handled automatically – the pairwise uniqueness
  clauses forbid selecting both copies.

The reduction runs in polynomial time: we examine each element and each set
once, and generate at most ``O(u * s^2)`` clauses where ``s`` is the maximum
number of sets containing a single element (bounded by the total number of
sets).
"""

from __future__ import annotations

from itertools import combinations
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
    # Validate the source instance – will raise InvalidInstance if malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)  # number of variables in the SAT formula

    # Mapping from element to list of set indices (1‑based) that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets, start=1):
        for e in s:
            # Elements are guaranteed to be within 0..u-1 by validation.
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # For each element, add the coverage clause and the pairwise uniqueness
    # clauses.
    for e in range(u):
        containing = element_to_sets[e]
        if not containing:
            # No set covers this element – the instance is unsatisfiable.
            # An empty clause makes the whole CNF unsatisfiable.
            clauses.append([])
            continue
        # At‑least‑one clause (positive literals).
        clauses.append(containing.copy())
        # At‑most‑one clauses: for each pair add (¬i ∨ ¬j).
        for i, j in combinations(containing, 2):
            clauses.append([-i, -j])

    # The SAT class does not require that every variable appears in a clause.
    # Returning the number of variables and the constructed clause list is
    # sufficient.
    sat_instance = {"num_vars": m, "clauses": clauses}
    # Validate the target instance for good measure (helps catch bugs).
    Sat.validate(sat_instance)
    return sat_instance

