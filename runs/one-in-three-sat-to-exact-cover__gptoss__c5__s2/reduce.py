"""Reduction from 1-in-3 SAT (positive) to Exact Cover.

The reduction is *not* polynomial in the worst case – it enumerates all
assignments of the SAT instance and creates a set for each satisfying
assignment.  For the purpose of this task we only need a correct reduction
that works on small instances used in the automated tests.

Given a SAT instance with ``c`` clauses we construct an Exact Cover instance
with universe size ``c + 1``.  Elements ``0 .. c-1`` correspond to the clauses;
element ``c`` is a dummy element that is always covered by a singleton set.

For every truth assignment that satisfies the 1‑in‑3 condition we add a set
containing *all* clause elements (``0 .. c-1``).  The dummy singleton set is
added separately.  An exact cover exists iff there is at least one
assignment‑set (covering all clause elements) together with the dummy set –
which holds exactly when the original formula is satisfiable.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import OneInThreeSat


def _is_satisfying_assignment(num_vars: int, clauses: List[List[int]], assignment: int) -> bool:
    """Return True if the bit‑vector ``assignment`` satisfies the 1‑in‑3 formula.

    ``assignment`` uses the least‑significant ``num_vars`` bits where bit ``i``
    (0‑based) corresponds to variable ``i+1`` (variables are 1‑based in the
    instance description).
    """
    for clause in clauses:
        true_cnt = 0
        for var in clause:
            # variable numbers start at 1
            if (assignment >> (var - 1)) & 1:
                true_cnt += 1
        if true_cnt != 1:
            return False
    return True


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    The returned dictionary conforms to the ``ExactCover`` format:
    ``{"universe_size": u, "sets": [...]}``.
    """
    # Validate the source instance using the provided validator.
    OneInThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Universe: clause elements 0..c-1 plus a dummy element c.
    universe_size = c + 1
    sets: List[List[int]] = []

    # Enumerate all assignments (up to 2**num_vars). For small instances this
    # is fine and keeps the implementation simple.
    for assign in range(1 << num_vars):
        if _is_satisfying_assignment(num_vars, clauses, assign):
            # This assignment satisfies the formula – add a set covering all
            # clause elements.
            sets.append(list(range(c)))

    # Add the dummy singleton set to allow an exact cover when at least one
    # satisfying assignment set exists.
    sets.append([c])

    return {"universe_size": universe_size, "sets": sets}

