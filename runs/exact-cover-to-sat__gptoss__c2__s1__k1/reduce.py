"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined by an instance dictionary::

    {"universe_size": u, "sets": [[element, ...], ...]}

where the universe consists of the integers ``0`` .. ``u-1`` and each
inner list is a subset of that universe.  The question is whether we can
choose a sub‑collection of the given sets such that every element of the
universe appears in **exactly one** chosen set (i.e. the chosen sets are
pairwise disjoint and their union is the whole universe).

The target problem (Sat) expects a conjunctive‑normal‑form formula
represented as::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered from ``1`` to ``m``.  A literal is a positive
integer ``v`` (meaning *v* is true) or a negative integer ``-v`` (meaning
*v* is false).  A clause is satisfied if at least one of its literals is
true.  An empty list of clauses is trivially satisfiable, while a clause
that is the empty list ``[]`` is never satisfiable.

The classic polynomial‑time reduction introduces a Boolean variable for
each set indicating whether the set is selected.  Two families of
constraints are then encoded as clauses:

1. **Cover each element** – for every element ``e`` the formula must contain
   a clause that asserts *at least one* of the sets containing ``e`` is
   chosen.
2. **Do not double‑cover** – for every pair of distinct sets that both
   contain the same element we add a clause forbidding them to be chosen
   simultaneously.

If an element is not contained in any set, the first family produces an
empty clause, correctly making the SAT instance unsatisfiable (and the
Exact‑Cover instance a “no”).  When the universe size is ``0`` there are no
such constraints, yielding a SAT instance with zero clauses, which is a
yes‑instance – matching the definition of Exact Cover.

The implementation below follows this construction.  It runs in time
polynomial in the size of the Exact‑Cover instance and produces a valid
SAT instance according to the format described above.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"``
        (list of list of ints) as specified in the problem statement.

    Returns
    -------
    dict
        A SAT instance with keys ``"num_vars"`` and ``"clauses"``.
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Number of Boolean variables equals the number of sets.
    m = len(sets)

    # For each element, collect the indices (1‑based) of sets that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        var = idx + 1  # SAT variables are 1‑based.
        for e in s:
            # Guard against malformed input (e outside 0..u-1); we assume
            # the provided validator would reject such instances, but we
            # simply ignore out‑of‑range elements to keep the reduction safe.
            if 0 <= e < u:
                element_to_sets[e].append(var)

    clauses: List[List[int]] = []

    # 1. At‑least‑one clause for each element.
    for e in range(u):
        vars_containing = element_to_sets[e]
        # If the list is empty we add an empty clause, which makes the SAT
        # instance unsatisfiable – exactly what we need.
        clauses.append(vars_containing.copy())

        # 2. Pairwise at‑most‑one constraints for this element.
        n = len(vars_containing)
        for i in range(n):
            vi = vars_containing[i]
            for j in range(i + 1, n):
                vj = vars_containing[j]
                # Clause (¬vi ∨ ¬vj)
                clauses.append([-vi, -vj])

    # Edge case: when u == 0 there are no element constraints, so ``clauses``
    # stays empty – a trivially satisfiable SAT instance.

    return {"num_vars": m, "clauses": clauses}

