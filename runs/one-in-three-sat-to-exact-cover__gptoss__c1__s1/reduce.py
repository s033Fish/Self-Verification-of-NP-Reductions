"""Reduction from One-In-Three SAT to Exact Cover.

The source problem (OneInThreeSat) instance format is:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause lists three distinct positive variable indices (1‑based).

The target problem (ExactCover) instance format is:
    {"universe_size": u, "sets": [[element, ...], ...]}
where the universe consists of the elements 0..u‑1.

Reduction idea:
    * Treat each clause as an element of the universe.
    * For each variable v (1‑based) create a set containing exactly the indices
      of the clauses in which v appears.
    * Selecting a variable's set corresponds to setting that variable to true;
      the set then covers all clauses where the variable appears.
    * An exact cover of the clause indices therefore picks a collection of
      variables such that every clause is covered exactly once, i.e. each
      clause has exactly one true variable.

Correctness:
    - If the SAT instance is satisfiable, let T be the set of variables set to
      true. For each clause, exactly one variable from T appears, so the
      clause index belongs to exactly one of the corresponding variable sets.
      Thus the collection {set(v) | v in T} is an exact cover.
    - Conversely, any exact cover selects a collection of variable sets that
      partition the clause indices. Assign those variables true and the rest
      false. Each clause is covered by exactly one selected set, guaranteeing
      exactly one true literal per clause.

The reduction runs in time O(m + |clauses|) and produces a valid ExactCover
instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        above.

    Returns
    -------
    dict
        An ExactCover instance with ``"universe_size"`` equal to the number
        of clauses and ``"sets"`` containing one set per variable. Each set is
        a list of clause indices (0‑based) where that variable appears.
    """
    num_vars: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Universe size is the number of clauses.
    universe_size = len(clauses)

    # Prepare a list for each variable to collect the clause indices it
    # appears in. Variables are 1‑based in the input, we store in a 0‑based
    # list for convenience.
    var_to_clauses: List[List[int]] = [[] for _ in range(num_vars)]

    for idx, clause in enumerate(clauses):
        for var in clause:
            # Guard against out‑of‑range variables (should not happen if input
            # is validated).
            if 1 <= var <= num_vars:
                var_to_clauses[var - 1].append(idx)

    # The ExactCover instance expects a list of sets (each a list of elements).
    # Empty sets are allowed; they simply will never be chosen in a solution.
    sets: List[List[int]] = var_to_clauses

    return {"universe_size": universe_size, "sets": sets}

