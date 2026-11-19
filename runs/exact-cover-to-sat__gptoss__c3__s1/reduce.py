"""Reduction from Exact Cover to SAT.

The source problem is defined in :class:`problems.ExactCover` and the target
in :class:`problems.Sat`.  An instance of Exact Cover is a dictionary
``{"universe_size": u, "sets": [[e, ...], ...]}`` where the universe consists
of the integers ``0..u-1``.  We create a Boolean variable for each set and
encode the requirement that every element is covered by *exactly one* chosen
set.

For each element ``e`` we add:

* **At‑least‑one** clause – the disjunction of all variables whose set
  contains ``e``.
* **At‑most‑one** clauses – for every pair of such variables we add a clause
  ``(-xi ∨ -xj)`` preventing both from being true simultaneously.

If an element has no covering set we emit an empty clause ``[]`` which is
unsatisfiable, correctly reflecting that the Exact Cover instance is a ``no``.

The reduction runs in time polynomial in the size of the input (quadratic in
the maximum number of sets covering a single element, which is bounded by the
total number of sets).  The returned instance follows the SAT format expected
by :class:`problems.Sat`.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat  # Imported for validation only.


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the Exact Cover specification.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [[lit, ...], ...]}``.
    """
    # Validate the source instance to guarantee correct format.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m: int = len(sets)  # number of variables in the SAT formula

    clauses: List[List[int]] = []

    # For each element of the universe, enforce that exactly one selected set
    # contains it.
    for e in range(u):
        covering: List[int] = [i + 1 for i, s in enumerate(sets) if e in s]

        # At‑least‑one: the element must appear in some chosen set.
        # If covering is empty we add an empty clause which makes the formula
        # unsatisfiable – this correctly mirrors the fact that the Exact Cover
        # instance cannot be satisfied.
        clauses.append(covering)

        # At‑most‑one: no two different covering sets may both be selected.
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                clauses.append([-covering[i], -covering[j]])

    # The SAT instance may contain zero variables (m == 0).  This is allowed by
    # the SAT specification and corresponds to a trivially satisfiable formula
    # when there are no clauses (the universe size is 0) or an unsatisfiable
    # one when an empty clause was added.
    return {"num_vars": m, "clauses": clauses}

