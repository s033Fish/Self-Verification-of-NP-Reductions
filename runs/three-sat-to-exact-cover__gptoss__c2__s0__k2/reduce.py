"""Reduction from 3‑SAT to Exact Cover.

The source problem is :class:`ThreeSat` (see ``problems.py``).  An instance is a
dictionary with keys ``"num_vars"`` and ``"clauses"`` where each clause is a list
of three signed integers.  The target problem is :class:`ExactCover`.  Its
instance format is ``{"universe_size": u, "sets": [[e, ...], ...]}``.

We implement the classic polynomial‑time reduction that encodes a truth
assignment as a selection of variable‑sets and uses clause‑sets to guarantee
that each clause is satisfied.

Construction
=============

*Universe elements*
    - For every variable ``i`` (1‑based) we create a *variable element* ``v_i``.
    - For every clause ``j`` we create a *clause element* ``c_j``.
    - For every literal occurrence (the appearance of a literal in a clause) we
      create a distinct *occurrence element* ``o_{j,ℓ}``.

*Sets*
    - **Variable sets** – for each variable ``i`` we create two sets:

        - ``T_i`` (variable is *true*): ``{v_i}`` together with all occurrence
          elements that correspond to *negative* literals ``-i``.
        - ``F_i`` (variable is *false*): ``{v_i}`` together with all occurrence
          elements that correspond to *positive* literals ``+i``.

      The element ``v_i`` appears in both sets, therefore an exact cover can
      contain at most one of them, forcing a consistent truth assignment.

    - **Clause sets** – for each clause ``j`` and each literal ``ℓ`` in that
      clause we create a set ``C_{j,ℓ}`` containing the clause element ``c_j``
      and the occurrence element for that literal.

*Correctness sketch*
    - ``v_i`` must be covered, so exactly one of ``T_i`` or ``F_i`` is chosen.
      If ``T_i`` is chosen, all negative occurrences of ``i`` are already
      covered, meaning no clause can use a negative literal of ``i`` (the
      corresponding clause set would double‑cover the occurrence element).  Thus
      any clause set that is selected must use a literal consistent with the
      chosen assignment.
    - Each clause element ``c_j`` must be covered, forcing the exact cover to
      pick exactly one of the three clause sets belonging to clause ``j``.
    - An occurrence element appears in exactly two sets: the clause set for
      that literal and the variable set of the *opposite* polarity.  Consequently,
      the occurrence is covered either by the clause set (meaning the clause is
      satisfied by that literal) or by the variable set (meaning the literal is
      not used).  The construction guarantees that a satisfying assignment of the
      SAT formula yields an exact cover and vice‑versa.

The reduction runs in time linear in the number of literals (``3 * #clauses``),
which is polynomial in the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of signed integers).

    Returns
    -------
    dict
        An Exact Cover instance ``{"universe_size": u, "sets": [...]}``.
    """

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Assign IDs for universe elements.
    # Order: variable elements, clause elements, occurrence elements.
    next_id = 0
    var_elem_ids: List[int] = []
    for _ in range(num_vars):
        var_elem_ids.append(next_id)
        next_id += 1

    clause_elem_ids: List[int] = []
    for _ in range(len(clauses)):
        clause_elem_ids.append(next_id)
        next_id += 1

    # For each literal occurrence we need a distinct element.
    # We'll store a mapping (clause_index, literal_index) -> occ_id.
    occ_ids: List[List[int]] = []  # parallel to clauses, each inner list length 3
    for clause in clauses:
        occ_row: List[int] = []
        for _ in clause:
            occ_row.append(next_id)
            next_id += 1
        occ_ids.append(occ_row)

    # Build sets.
    sets: List[List[int]] = []

    # Variable sets.
    # For each variable i (1‑based), collect occurrence ids of positive and negative literals.
    pos_occ: List[List[int]] = [[] for _ in range(num_vars)]
    neg_occ: List[List[int]] = [[] for _ in range(num_vars)]
    for c_idx, clause in enumerate(clauses):
        for lit_idx, lit in enumerate(clause):
            var = abs(lit) - 1  # zero‑based variable index
            occ_id = occ_ids[c_idx][lit_idx]
            if lit > 0:
                pos_occ[var].append(occ_id)
            else:
                neg_occ[var].append(occ_id)

    for i in range(num_vars):
        var_id = var_elem_ids[i]
        # True set covers negative occurrences (cannot use them)
        true_set = [var_id] + neg_occ[i]
        false_set = [var_id] + pos_occ[i]
        sets.append(true_set)
        sets.append(false_set)

    # Clause sets.
    for c_idx, clause in enumerate(clauses):
        clause_id = clause_elem_ids[c_idx]
        for lit_idx, _ in enumerate(clause):
            occ_id = occ_ids[c_idx][lit_idx]
            sets.append([clause_id, occ_id])

    universe_size = next_id
    return {"universe_size": universe_size, "sets": sets}

