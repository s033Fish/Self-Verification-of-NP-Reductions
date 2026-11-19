"""Reduction from 1-in-3 SAT (OneInThreeSat) to Exact Cover.

The reduction is polynomial and very simple:

* Universe elements correspond to the clauses of the SAT instance.
* For each variable v (1‑based indexing) we create a set containing the
  indices of the clauses in which v appears.
* Selecting a variable's set means assigning the variable **true**. The
  exact‑cover condition that every universe element (clause) is covered
  exactly once enforces that each clause has exactly one true variable.
* Variables that are not selected are interpreted as **false**.  Empty
  sets (variables that never appear) are harmless – they can never be
  chosen in a valid exact cover.

Formally, given an instance ``{"num_vars": m, "clauses": C}`` where
``C`` is a list of length *u*, we output ``{"universe_size": u,
"sets": S}`` where ``S`` is a list of *m* sets and the i‑th set (for
variable i+1) is ``[j for j, clause in enumerate(C) if i+1 in clause]``.

The reduction runs in O(m·u) time and produces a valid ExactCover
instance according to ``ExactCover.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"``
        (list of three‑element lists of ints).

    Returns
    -------
    dict
        An ExactCover instance with keys ``"universe_size"`` and
        ``"sets"`` as described in the module docstring.
    """
    # Extract data
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Universe size is the number of clauses
    u = len(clauses)

    # Build sets for each variable 1..m
    sets: List[List[int]] = []
    for var in range(1, m + 1):
        # Collect clause indices where this variable appears
        indices: List[int] = [i for i, clause in enumerate(clauses) if var in clause]
        sets.append(indices)

    return {"universe_size": u, "sets": sets}

