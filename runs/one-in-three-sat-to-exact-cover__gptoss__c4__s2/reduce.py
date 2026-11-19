"""Reduction from 1-in-3 SAT (positive) to Exact Cover.

The reduction is classic and runs in polynomial time.

For a given OneInThreeSat instance with ``m`` variables and ``k`` clauses we
create a universe consisting of ``m`` variable elements and ``k`` clause
elements.  For each variable ``x`` we create two sets:

* ``T_x`` – the *true* set.  It contains the variable element ``v_x`` and the
  clause element for every clause that contains ``x``.  Selecting this set
  corresponds to assigning ``x = True`` – it covers all clause elements that
  rely on ``x`` being the unique true literal in those clauses.
* ``F_x`` – the *false* set.  It contains only the variable element ``v_x``.
  Selecting this set corresponds to assigning ``x = False``.

In any exact cover we must cover each variable element exactly once, which
forces us to pick exactly one of ``T_x`` or ``F_x`` for each variable ``x``.
Clause elements are covered only by the ``T_x`` sets of the variables that
appear in the clause.  Because each clause element must be covered exactly
once, exactly one of the three variables in the clause must be assigned true.

Thus a satisfying assignment for the 1‑in‑3‑SAT instance exists iff the
constructed Exact Cover instance has a solution.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, ExactCover


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined by
        :class:`OneInThreeSat`.

    Returns
    -------
    dict
        An Exact Cover instance (dictionary with keys ``"universe_size"`` and
        ``"sets"``).
    """
    # Validate source instance (will raise if malformed)
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k = len(clauses)

    # Universe: first m elements correspond to variables (0 .. m-1),
    # next k elements correspond to clauses (m .. m+k-1).
    universe_size = m + k

    # Build a mapping from variable to the list of clause indices it appears in.
    var_to_clauses: List[List[int]] = [[] for _ in range(m + 1)]  # 1‑based vars
    for idx, clause in enumerate(clauses):
        for var in clause:
            var_to_clauses[var].append(idx)

    sets: List[List[int]] = []
    # For each variable create the true and false sets.
    for var in range(1, m + 1):
        var_elem = var - 1  # variable element index in universe
        # True set includes the variable element and all clause elements where var appears.
        true_set = [var_elem]
        for clause_idx in var_to_clauses[var]:
            true_set.append(m + clause_idx)
        false_set = [var_elem]
        sets.append(true_set)
        sets.append(false_set)

    target_instance = {"universe_size": universe_size, "sets": sets}
    # Validate target instance for safety (optional, can be omitted in final version)
    ExactCover.validate(target_instance)
    return target_instance

