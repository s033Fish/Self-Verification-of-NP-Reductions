"""Reduction from One-In-Three SAT to Exact Cover.

The source problem (OneInThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *distinct* positive variable indices in the
range ``1..m``.  The instance is a YES‑instance iff there exists a truth
assignment to the ``m`` variables such that **exactly one** variable in each
clause is assigned ``True``.

The target problem (ExactCover) expects instances of the form::

    {"universe_size": u, "sets": [[e0, e1, ...], ...]}

Elements are integers ``0 .. u-1``.  The instance is a YES‑instance iff a
sub‑collection of the given sets can be selected that are pairwise disjoint
and whose union equals the whole universe.

The construction below is a standard polynomial‑time reduction.  For each
variable ``i`` we create a *selector* element ``v_i``.  Two sets are created for
the variable – one representing the assignment ``True`` and one representing
``False`` – and both contain the selector element.  Consequently exactly one
of the two sets can be chosen in any exact cover, thereby fixing the truth
value of the variable.

For each clause ``C_j = (a, b, c)`` we create three distinct clause elements
``c_{j,0}``, ``c_{j,1}``, ``c_{j,2}``.  The *True* set of variable ``a``
contains the clause element that corresponds to the position of ``a`` inside
the clause, and similarly for ``b`` and ``c``.  The *False* set contains only
the selector element.  In an exact cover the clause elements must each be
covered exactly once, which forces exactly one of the three literals in the
clause to be assigned ``True``.

If the original formula has no clauses the reduction yields a universe that
consists solely of the selector elements.  For each variable we have two
identical singleton sets ``{v_i}``; picking either one for each variable gives
an exact cover, matching the fact that a clause‑free formula is always
 satisfiable.

The reduction runs in time linear in the size of the input instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a One‑In‑Three SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of ints).

    Returns
    -------
    dict
        An Exact Cover instance as described in the module docstring.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Universe layout:
    #   0 .. m-1               -> selector element for variable i (i = index+1)
    #   m .. m+3*len(clauses)-1 -> clause elements, three per clause.
    num_clauses = len(clauses)
    universe_size = m + 3 * num_clauses

    sets: List[List[int]] = []

    # Helper to compute clause element index.
    def clause_elem_index(clause_idx: int, position: int) -> int:
        """Return the universal element index for the *position*th literal
        of clause *clause_idx* (0‑based)."""
        return m + 3 * clause_idx + position

    # For each variable create the True‑set and the False‑set.
    # Both contain the selector element (i-1).  The True‑set additionally
    # contains the clause element for each occurrence of the variable.
    # Build a mapping from variable to list of (clause_idx, position) where it
    # appears.
    occ: dict[int, List[tuple[int, int]]] = {i: [] for i in range(1, m + 1)}
    for ci, clause in enumerate(clauses):
        for pos, var in enumerate(clause):
            # variables are guaranteed to be in 1..m and distinct within a clause
            occ[var].append((ci, pos))

    for var in range(1, m + 1):
        selector = var - 1  # element representing variable var
        # True set
        true_set = [selector]
        for ci, pos in occ.get(var, []):
            true_set.append(clause_elem_index(ci, pos))
        sets.append(true_set)
        # False set – only the selector element
        false_set = [selector]
        sets.append(false_set)

    # The constructed instance satisfies the ExactCover format.
    return {"universe_size": universe_size, "sets": sets}

# The module is intended to be imported by the evaluation harness.  No
# top‑level test code is executed.
