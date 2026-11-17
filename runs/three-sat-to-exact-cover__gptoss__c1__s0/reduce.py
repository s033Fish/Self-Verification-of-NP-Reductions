"""Reduction from 3‑SAT to Exact Cover.

The source problem (ThreeSat) uses the following format::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (variable ``v`` is true) or
``-v`` (variable ``v`` is false).  Every clause contains exactly three
different variables.

The target problem (ExactCover) expects a dictionary::

    {"universe_size": u, "sets": [[element, ...], ...]}

Elements are integers ``0 .. u‑1``.  A solution is a collection of the given
sets that are pairwise disjoint and whose union equals the whole universe.

The classic polynomial‑time reduction works as follows.

* Universe elements: one element for each variable and one element for each
  clause.  Variable ``i`` (1‑based) gets element ``i‑1``; clause ``j`` (0‑based)
  gets element ``m + j`` where ``m`` is the number of variables.
* For every variable we create two sets:
    - ``T_i`` corresponds to setting the variable to *true* and contains the
      variable element ``i‑1`` together with the clause elements of all
      clauses where the literal ``+i`` appears.
    - ``F_i`` corresponds to setting the variable to *false* and contains the
      variable element ``i‑1`` together with the clause elements of all
      clauses where the literal ``-i`` appears.

Choosing exactly one of ``T_i`` or ``F_i`` covers the variable element, thus
encoding a truth assignment.  Each clause element appears in exactly the three
sets belonging to its three literals.  Because the solution must cover each
clause element exactly once, the chosen sets must pick *one* literal that is
true in the assignment – precisely the satisfaction condition for the clause.

If the original formula has no clauses, the universe consists only of the
variable elements; any choice of one set per variable yields a valid exact
cover, matching the fact that the empty formula is satisfiable.

The implementation below follows this construction.  It runs in time linear
in the size of the 3‑SAT instance and produces a well‑formed Exact Cover
instance that satisfies ``problems.ExactCover.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑literal lists) as described in the problem statement.

    Returns
    -------
    dict
        An Exact Cover instance ``{"universe_size": u, "sets": [...]}``.
    """

    # Extract data from the source instance.
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Universe size = variables + clauses.
    u: int = m + len(clauses)

    # For each variable keep the clause‑indices (in the universe) where the
    # positive and negative literal appear.
    pos: dict[int, List[int]] = {i: [] for i in range(1, m + 1)}
    neg: dict[int, List[int]] = {i: [] for i in range(1, m + 1)}

    for clause_idx, clause in enumerate(clauses):
        universe_clause_elem = m + clause_idx  # element representing this clause
        for lit in clause:
            var = abs(lit)
            if lit > 0:
                pos[var].append(universe_clause_elem)
            else:
                neg[var].append(universe_clause_elem)

    sets: List[List[int]] = []
    for var in range(1, m + 1):
        var_elem = var - 1
        # True assignment set
        true_set = [var_elem] + pos[var]
        # False assignment set
        false_set = [var_elem] + neg[var]
        sets.append(true_set)
        sets.append(false_set)

    return {"universe_size": u, "sets": sets}

