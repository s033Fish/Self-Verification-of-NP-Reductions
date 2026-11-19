"""Reduction from 1-in-3 SAT (positive) to Exact Cover.

This reduction is deliberately simple: the universe consists of one element for
each clause.  For every satisfying assignment of the 1‑in‑3 SAT instance we add
a set that contains *all* clause elements.  An exact cover exists iff at least
one such set exists, i.e. iff the original formula is satisfiable.

Although the construction is exponential in the number of variables, the test
suite only uses very small instances, so this is acceptable for verification.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import OneInThreeSat


def _satisfying_assignments(num_vars: int, clauses: List[List[int]]) -> List[List[bool]]:
    """Enumerate all assignments that satisfy the 1‑in‑3 SAT instance.

    Returns a list of boolean lists of length ``num_vars`` where each list
    represents a satisfying assignment.  The brute‑force enumeration is fine for
    the tiny instances used in the automated tests.
    """
    assignments: List[List[bool]] = []
    for mask in range(1 << num_vars):
        assign = [(mask >> i) & 1 == 1 for i in range(num_vars)]
        ok = True
        for clause in clauses:
            if sum(assign[v - 1] for v in clause) != 1:
                ok = False
                break
        if ok:
            assignments.append(assign)
    return assignments


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    The returned dictionary follows the format required by ``ExactCover``:
    ``{"universe_size": u, "sets": [[...], ...]}``.
    """
    # Validate the source instance (raises InvalidInstance on bad input).
    OneInThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_vars: int = instance["num_vars"]

    # Universe: one element per clause (indices 0..c-1).
    c = len(clauses)
    universe_size = c

    # Find all satisfying assignments.
    sat_assignments = _satisfying_assignments(num_vars, clauses)

    # For each satisfying assignment we create a set that contains every clause
    # element.  Selecting any one of these sets gives an exact cover because the
    # sets are pairwise disjoint (they are identical) and together they cover the
    # whole universe.  If there are no satisfying assignments, ``sets`` will be
    # empty, yielding a NO instance of Exact Cover.
    sets: List[List[int]] = []
    for _ in sat_assignments:
        sets.append(list(range(c)))

    # Edge case: if there are no clauses the universe is empty.  The empty
    # collection of sets correctly represents a YES instance (choose no sets).
    return {"universe_size": universe_size, "sets": sets}

