"""Reduction from 3‑SAT (SOURCE) to Exact Cover (TARGET).

The reduction follows the classic polynomial‑time construction used in
Karp's NP‑completeness proofs.  Given a 3‑SAT instance with ``m`` variables
and ``c`` clauses, we create an Exact Cover instance as follows:

* Universe elements
    - For each clause ``j`` (``0 <= j < c``) we create a *clause element*
      ``C_j``.
    - For each literal occurrence (a literal appearing in a specific clause)
      we create an *occurrence element* ``O_k``.  The total number of
      occurrences is ``3*c`` because every clause contains exactly three
      literals.
    The universe size is therefore ``c + 3*c``.

* Sets
    1. **Clause sets** – For each literal occurrence belonging to clause ``j``
       we add the set ``{C_j, O_k}``.  Selecting this set means that clause ``j``
       is satisfied by that literal, and the corresponding occurrence element
       is covered.
    2. **Variable consistency sets** – For each variable ``x`` we create two
       sets:
          * ``T_x`` – the set of *all* occurrence elements that correspond to
            the *positive* literal ``+x``.
          * ``F_x`` – the set of *all* occurrence elements that correspond to
            the *negative* literal ``-x``.
       Exactly one of ``T_x`` or ``F_x`` will be chosen in any exact cover.
       If ``T_x`` is chosen, all positive occurrences are already covered, so
       no clause can use a positive literal of ``x``; this forces the assignment
       ``x = false``.  Conversely, choosing ``F_x`` corresponds to setting the
       variable to ``true``.

The constructed instance has the property that a collection of disjoint sets
covers the whole universe iff the original formula is satisfiable:

* Every clause element must be covered, so each clause picks exactly one of its
  three literals.
* Every occurrence element is covered either by the clause set that uses it or
  by the appropriate variable‑consistency set.
* Because the consistency sets contain *all* occurrences of the same sign, a
  variable cannot be used both positively and negatively – the exact cover
  forces a consistent truth assignment.

Edge cases:
    - If there are no clauses, the universe is empty and the Exact Cover
      instance is trivially a yes‑instance, matching the fact that an empty 3‑SAT
      formula is satisfiable.
    - Variables that never appear generate empty consistency sets; such sets
      are harmless because they are never needed to cover any element.

The implementation below follows this construction and runs in time linear in
the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance: dict
        A 3‑SAT instance with keys ``"num_vars"`` (int) and ``"clauses"``
        (list of three‑element lists of literals).  Literals are encoded as
        signed integers, e.g. ``+3`` for variable 3 being true and ``-2`` for
        variable 2 being false.

    Returns
    -------
    dict
        An Exact Cover instance with keys ``"universe_size"`` and ``"sets"``.
    """

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Number of clauses
    c = len(clauses)

    # Assign universe indices:
    #   0 .. c-1          -> clause elements C_j
    #   c .. c+occ-1      -> occurrence elements O_k
    # There are exactly 3*c occurrences because each clause has 3 literals.
    clause_offset = 0
    occ_offset = c

    # Build mapping from (clause_index, literal_position) to occurrence id
    # and also collect occurrence ids per variable sign.
    # For each variable we keep two lists: positive_occurrences and negative_occurrences.
    pos_occ: List[List[int]] = [[] for _ in range(num_vars + 1)]  # 1‑based indexing
    neg_occ: List[List[int]] = [[] for _ in range(num_vars + 1)]

    sets: List[List[int]] = []

    occ_id = 0
    for j, clause in enumerate(clauses):
        clause_elem = clause_offset + j
        for lit in clause:
            var = abs(lit)
            # occurrence element index
            occ_elem = occ_offset + occ_id
            # Clause set {C_j, O_k}
            sets.append([clause_elem, occ_elem])
            # Record occurrence for variable consistency sets
            if lit > 0:
                pos_occ[var].append(occ_elem)
            else:
                neg_occ[var].append(occ_elem)
            occ_id += 1

    # Variable consistency sets
    for var in range(1, num_vars + 1):
        if pos_occ[var]:
            sets.append(pos_occ[var][:])  # copy to avoid mutation later
        if neg_occ[var]:
            sets.append(neg_occ[var][:])

    universe_size = c + occ_id  # occ_id == 3*c

    return {"universe_size": universe_size, "sets": sets}

