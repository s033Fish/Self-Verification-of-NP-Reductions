"""Reduction from 1-in-3 SAT to Exact Cover.

The source problem (OneInThreeSat) instance format is:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause lists three distinct positive variable indices (1‑based).

The target problem (ExactCover) instance format is:
    {"universe_size": u, "sets": [[element, ...], ...]}
where the universe consists of the elements 0..u‑1.

Reduction idea
----------------
We treat each clause as an element of the universe. For every variable i we
create a set containing exactly those clause indices in which i appears.
Selecting a collection of these variable‑sets that forms an exact cover means
that each clause is covered by **exactly one** selected variable, i.e. exactly
one of its three literals is assigned true. Variables whose sets are not
selected are assigned false. This correspondence is a classic reduction and
preserves the yes‑instance property.

Edge cases
~~~~~~~~~~
* If there are no clauses, the universe size is 0. Any assignment (including
  the empty one) satisfies the formula, and Exact Cover with an empty
  universe is trivially a yes‑instance.
* Variables that never appear in any clause produce an empty set. Empty sets
  are ignored by the Exact Cover definition (they never affect the cover),
  so we may include them or omit them. Here we omit them for brevity.

The reduction runs in linear time in the size of the input (O(m + n) where
`n` is the number of clauses).
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of variable indices, 1‑based).

    Returns
    -------
    dict
        An ExactCover instance with ``"universe_size"`` equal to the number of
        clauses and ``"sets"`` containing, for each variable that appears in at
        least one clause, the list of clause indices where it occurs.
    """

    num_vars: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Universe consists of clause indices 0..n-1
    universe_size = len(clauses)

    # Mapping from variable (1‑based) to list of clause indices where it appears
    var_to_clauses: List[List[int]] = [[] for _ in range(num_vars + 1)]  # index 0 unused
    for idx, clause in enumerate(clauses):
        for var in clause:
            # Safety: ignore out‑of‑range variables (should not happen after validation)
            if 1 <= var <= num_vars:
                var_to_clauses[var].append(idx)

    # Build the list of sets, omitting empty sets (variables that never appear)
    sets: List[List[int]] = [sorted(lst) for lst in var_to_clauses[1:] if lst]

    return {"universe_size": universe_size, "sets": sets}

