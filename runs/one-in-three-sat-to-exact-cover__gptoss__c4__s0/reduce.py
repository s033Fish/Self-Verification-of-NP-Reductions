"""Reduction from 1-in-3 SAT (positive) to Exact Cover.

The reduction follows the classic construction:
* For each clause we create a unique element C_i.
* For each occurrence of a variable in a clause we create a unique element O_{i,j}.
* For each literal occurrence we create a set {C_i, O_{i,j}}.
* For each variable x we create a set containing all occurrence elements O_{i,j}
  where x appears. (If x does not appear, the set is empty and can be omitted.)

An exact cover selects, for each clause, exactly one of its three literal sets.
If the set for variable x in clause i is chosen, the occurrence element O_{i,j}
is covered by that set, so the variable‑set V_x cannot be chosen.  Thus the
chosen literal’s variable is interpreted as *true* in that clause.  If V_x is
chosen, none of the literal sets using x can be chosen, meaning x is *false*
everywhere it appears.  This yields a one‑to‑one correspondence between exact
covers and satisfying assignments of the 1‑in‑3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, ExactCover


def reduce(instance: Dict) -> Dict:
    """Reduce a positive 1‑in‑3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance: dict with keys "num_vars" and "clauses" as defined by
        :class:`OneInThreeSat`.

    Returns
    -------
    dict
        A valid Exact Cover instance equivalent to the input.
    """
    # Validate source instance.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Universe elements:
    #   0 .. num_clauses-1   -> clause elements C_i
    #   num_clauses .. ...   -> occurrence elements O_{i,j}
    clause_offset = 0
    occ_offset = num_clauses
    occ_index_map: dict[tuple[int, int], int] = {}
    current = occ_offset
    for ci, clause in enumerate(clauses):
        for pos in range(3):  # each clause has exactly three literals
            occ_index_map[(ci, pos)] = current
            current += 1
    total_universe = current

    sets: List[List[int]] = []

    # Literal sets: {C_i, O_{i,j}} for each literal in each clause
    for ci, clause in enumerate(clauses):
        clause_elem = clause_offset + ci
        for pos, var in enumerate(clause):
            occ_elem = occ_index_map[(ci, pos)]
            sets.append([clause_elem, occ_elem])

    # Variable sets: all occurrence elements where the variable appears
    var_to_occ: dict[int, List[int]] = {v: [] for v in range(1, m + 1)}
    for ci, clause in enumerate(clauses):
        for pos, var in enumerate(clause):
            occ_elem = occ_index_map[(ci, pos)]
            var_to_occ[var].append(occ_elem)

    for var, occs in var_to_occ.items():
        if occs:  # ignore empty sets
            sets.append(occs)

    return {"universe_size": total_universe, "sets": sets}

