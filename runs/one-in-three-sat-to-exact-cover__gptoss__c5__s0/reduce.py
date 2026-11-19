"""Reduction from 1-in-3 SAT (OneInThreeSat) to Exact Cover.

The reduction creates an Exact Cover instance that encodes the requirement that
each clause has exactly one true variable and that a variable is assigned a
consistent truth value across all its occurrences.

Construction
------------
* Universe elements consist of:
  - One element for each clause (indices 0 .. C‑1).
  - One element for each *occurrence* of a variable in a clause.  These are
    assigned consecutive indices after the clause elements.
* Sets:
  1. For every occurrence (clause i, variable v) we create the set
     ``{ clause_i , occ_{i,v} }``.  Selecting this set means that variable v is the
     true literal of clause i.
  2. For each variable v we create a set containing **all** occurrence elements
     that involve v.  Selecting this set means that v is assigned false, which
     prevents any of its type‑1 sets from being chosen.

An exact cover must pick exactly one type‑1 set for each clause (covering the
clause element exactly once) and, for each occurrence element, either the
corresponding type‑1 set (making the variable true in that clause) or the
variable’s type‑2 set (making the variable false).  This yields a one‑to‑one
correspondence between satisfying assignments of the 1‑in‑3‑SAT instance and exact
covers of the constructed instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import OneInThreeSat, ExactCover


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance: dict
        A 1‑in‑3 SAT instance with keys ``"num_vars"`` and ``"clauses"``.

    Returns
    -------
    dict
        An ExactCover instance equivalent to the input.
    """
    # Validate source instance.
    OneInThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Map each (clause_index, variable) to a unique occurrence element.
    occ_id: dict[Tuple[int, int], int] = {}
    next_elem = num_clauses  # after clause elements
    for i, clause in enumerate(clauses):
        for var in clause:
            occ_id[(i, var)] = next_elem
            next_elem += 1

    universe_size = next_elem
    sets: List[List[int]] = []

    # Type‑1 sets: one per occurrence, linking clause element with occurrence.
    for (i, var), eid in occ_id.items():
        sets.append([i, eid])

    # Type‑2 sets: one per variable, covering all its occurrence elements.
    var_to_occ: dict[int, List[int]] = {v: [] for v in range(1, instance["num_vars"] + 1)}
    for (i, var), eid in occ_id.items():
        var_to_occ[var].append(eid)
    for var, occs in var_to_occ.items():
        if occs:  # a variable may not appear at all; an empty set is harmless
            sets.append(occs)

    reduced = {"universe_size": universe_size, "sets": sets}
    ExactCover.validate(reduced)
    return reduced

