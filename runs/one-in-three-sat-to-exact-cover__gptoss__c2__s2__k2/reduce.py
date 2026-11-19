"""Reduction from OneInThreeSat to ExactCover.

The source problem (OneInThreeSat) instance format:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
All variables are positive integers 1..m and each clause lists three distinct
variables.

The target problem (ExactCover) instance format:
    {"universe_size": u, "sets": [[element, ...], ...]}
Elements are integers 0..u-1.

Reduction construction (standard polynomial‑time reduction):
    * For each clause i we create a unique universe element c_i (0‑based).
    * For each occurrence of a variable v in a clause we create a distinct
      *slot* element s_{v,occurrence}. All slot elements together form the
      remainder of the universe.
    * For every occurrence (clause i, variable v) we add a set {c_i,
      s_{v,occurrence}}. Selecting this set means that clause i is satisfied
      by variable v and that the corresponding slot of v is used.
    * For each variable v we add one additional set containing *all* slot
      elements belonging to v. Selecting this set means that variable v is
      assigned FALSE; none of its occurrence sets are selected, and the slots
      are covered by this single set.

Exactly one set must be chosen for each clause element, guaranteeing that
each clause has exactly one true literal. For each variable, either all its
occurrence sets are chosen (assigning the variable TRUE) or the single "false"
set is chosen (assigning FALSE), because the slot elements must be covered
exactly once.

The construction runs in time polynomial in the size of the input (linear in
the number of clauses and variable occurrences).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance: dict with keys "num_vars" and "clauses" as described above.

    Returns
    -------
    dict with keys "universe_size" and "sets" representing the ExactCover
    instance.
    """

    num_vars = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Mapping from variable to list of its slot indices (to be filled).
    var_to_slots: Dict[int, List[int]] = {v: [] for v in range(1, num_vars + 1)}

    # First assign slot indices. We will number universe elements as follows:
    #   0 .. num_clauses-1            -> clause elements
    #   num_clauses ..                -> slot elements
    next_slot_index = num_clauses
    # For each clause and each variable in that clause, allocate a slot.
    for clause in clauses:
        for var in clause:
            # Ensure var is within 1..num_vars (validation is assumed elsewhere)
            var_to_slots.setdefault(var, []).append(next_slot_index)
            next_slot_index += 1

    total_universe = next_slot_index  # final count of elements
    sets: List[List[int]] = []

    # Add occurrence sets: one per (clause, variable) pair.
    for clause_idx, clause in enumerate(clauses):
        for var in clause:
            # Pop the first unused slot for this variable.
            slot = var_to_slots[var].pop(0)
            sets.append([clause_idx, slot])

    # Re‑collect slots per variable for the false sets.
    var_to_all_slots: Dict[int, List[int]] = {v: [] for v in range(1, num_vars + 1)}
    slot_counter = num_clauses
    for clause in clauses:
        for var in clause:
            var_to_all_slots[var].append(slot_counter)
            slot_counter += 1

    for var, slots in var_to_all_slots.items():
        if slots:  # only add if the variable actually occurs
            sets.append(slots)

    return {"universe_size": total_universe, "sets": sets}

