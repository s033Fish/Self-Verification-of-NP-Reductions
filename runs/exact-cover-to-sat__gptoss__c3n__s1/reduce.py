"""Reduction from Exact Cover to SAT.

The source problem is :class:`ExactCover` defined in ``problems.py``.  An
instance is a dictionary ``{"universe_size": u, "sets": [...]}`` where each
set lists distinct elements of the universe ``0..u-1``.

The target problem is :class:`Sat`.  An instance is a dictionary
``{"num_vars": m, "clauses": [...]}`` where each clause is a list of integer
*literals* ``+v`` (variable ``v`` is true) or ``-v`` (variable ``v`` is false).

The reduction creates a Boolean variable ``x_i`` for each set ``i`` in the
Exact‑Cover instance.  The SAT formula enforces that the chosen sets are a
partition of the universe:

* **Coverage** – for each element ``e`` of the universe we add a clause that
  at least one set containing ``e`` is chosen: ``(x_i1 ∨ x_i2 ∨ …)``.
* **Disjointness** – for any two distinct sets that both contain the same
  element we add a clause forbidding them to be chosen simultaneously:
  ``(¬x_i ∨ ¬x_j)``.

If the universe is empty ``u == 0`` the reduction produces a formula with no
clauses (which is satisfiable by definition) – matching the Exact‑Cover edge
case that an empty universe is a *yes* instance.

The construction is clearly polynomial‑time: we iterate over each element and
over each pair of sets that intersect on that element, which is ``O(u·n²)``
where ``n`` is the number of sets.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to :class:`ExactCover`'s format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n = len(sets)

    # Build a list of which sets contain each element.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    # Coverage clauses: each element must appear in at least one chosen set.
    for e in range(u):
        containing = element_to_sets[e]
        if not containing:
            # No set covers this element – the Exact Cover instance is a
            # guaranteed *no*; we encode this by adding an empty clause which
            # makes the SAT formula unsatisfiable.
            clauses.append([])
        else:
            # Clause (x_i1 ∨ x_i2 ∨ ...)
            clauses.append([i + 1 for i in containing])

    # Disjointness clauses: for any two distinct sets that share an element,
    # add (¬x_i ∨ ¬x_j).
    for e in range(u):
        containing = element_to_sets[e]
        # Add pairwise constraints for each unordered pair.
        for i in range(len(containing)):
            for j in range(i + 1, len(containing)):
                vi = containing[i] + 1
                vj = containing[j] + 1
                clauses.append([-vi, -vj])

    # The SAT instance may have zero variables (if there are no sets).  This
    # is allowed by the problem definition.
    sat_instance = {"num_vars": n, "clauses": clauses}
    # Validate the produced instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

