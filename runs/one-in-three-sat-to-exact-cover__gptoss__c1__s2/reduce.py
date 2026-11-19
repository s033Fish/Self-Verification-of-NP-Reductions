"""Reduction from OneInThreeSat to ExactCover.

The source instance format (OneInThreeSat):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    Variables are numbered 1..m. Each clause contains three distinct
    positive variables.

The target instance format (ExactCover):
    {"universe_size": u, "sets": [[element, ...], ...]}
    The universe consists of elements 0..u-1.

Reduction construction:
    * For each clause i we create a unique universe element C_i (indices
      0 .. num_clauses-1).
    * For each occurrence of a variable v in clause i we create a
      distinct occurrence element O_{v,i}. These get indices starting
      after the clause elements.
    * For every literal (v in clause i) we add a set {C_i, O_{v,i}}.
      Selecting this set means that clause i is satisfied by variable v.
    * For each variable v we add a selector set containing *all* its
      occurrence elements O_{v,i}.  This set is chosen exactly when the
      variable is assigned FALSE; if the variable is TRUE we must select
      all clause‑literal sets that contain its occurrence elements, which
      forces the selector set to be omitted.

Correctness sketch:
    - Each clause element C_i must be covered exactly once, so exactly
      one of its three literal sets is chosen.
    - If a variable v is assigned FALSE, its selector set covers all
      occurrence elements of v, preventing any clause set that includes
      those elements from being chosen.  Hence v does not appear in any
      satisfied clause.
    - If v is assigned TRUE, the selector set is not chosen.  To cover
      each occurrence element O_{v,i} we must select the corresponding
      clause set {C_i, O_{v,i}}.  Consequently v appears as the unique
      true literal in *all* clauses containing it, satisfying the
      1‑in‑3 condition.
    - Variables that never appear generate no occurrence elements; they
      impose no constraints, matching the source problem's semantics.

The construction runs in time polynomial in the size of the input.
"""

def reduce(instance):
    m = instance["num_vars"]
    clauses = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Clause elements: 0 .. num_clauses-1
    # Occurrence elements start after clause elements
    occurrence_id = {}
    next_id = num_clauses
    for i, clause in enumerate(clauses):
        for v in clause:
            occurrence_id[(v, i)] = next_id
            next_id += 1

    universe_size = next_id
    sets = []

    # Clause literal sets: each contains the clause element and the
    # corresponding occurrence element.
    for i, clause in enumerate(clauses):
        for v in clause:
            sets.append([i, occurrence_id[(v, i)]])

    # Variable selector sets: one per variable that actually appears.
    for v in range(1, m + 1):
        occ_ids = [occurrence_id[(v, i)] for i, cl in enumerate(clauses) if v in cl]
        if occ_ids:
            sets.append(occ_ids)
        # If a variable never appears, we add nothing (empty sets are
        # irrelevant for Exact Cover and would not affect correctness).

    return {"universe_size": universe_size, "sets": sets}

# The module provides only the reduce function as required.

