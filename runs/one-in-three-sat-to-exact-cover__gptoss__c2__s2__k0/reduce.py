"""Reduction from One-In-Three SAT (positive) to Exact Cover.

The source problem instance has the form:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause lists three distinct variable indices (1‑based).

The target Exact Cover instance must be of the form:
    {"universe_size": u, "sets": [[e0, e1, ...], ...]}
with universe elements 0..u‑1.

Reduction construction:
    * The universe consists of one element for each clause.  Element i
      corresponds to clause i (0‑based index).
    * For each variable j (1‑based) we create a set containing exactly the
      indices of the clauses in which variable j appears.
    * Variables that do not appear in any clause yield an empty set – such
      sets are harmless for Exact Cover because they can never be selected.

Correctness sketch:
    - Selecting a collection of sets that forms an exact cover means that
      each clause element is covered by exactly one variable‑set.  Hence each
      clause has exactly one variable whose set is chosen – that variable is
      interpreted as the true literal in the clause.
    - A variable may be true in several clauses because its set contains all
      clause indices where it appears; this does not violate the exact‑cover
      condition because each clause index is covered only once.
    - If a variable's set is not chosen, the variable is considered false.
    - Conversely, given a satisfying assignment of the 1‑in‑3‑SAT formula we
      select precisely the sets of the variables assigned true.  Every clause
      has exactly one true literal, so each clause element is covered exactly
      once, yielding a valid exact cover.

Both directions preserve satisfiability, and the construction runs in
polynomial time.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "num_vars" and "clauses" as described in the
        problem statement.

    Returns
    -------
    dict
        An ExactCover instance with keys "universe_size" and "sets".
    """
    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Universe size equals number of clauses
    u = len(clauses)

    # Prepare a list for each variable (1‑based indexing) to collect clause indices
    var_to_clauses: List[List[int]] = [[] for _ in range(m + 1)]  # index 0 unused

    for idx, clause in enumerate(clauses):
        # clause is a list of three distinct variable indices
        for var in clause:
            # Safety: ignore out‑of‑range variable numbers (should not happen in valid input)
            if 1 <= var <= m:
                var_to_clauses[var].append(idx)

    # Build the list of sets for the Exact Cover instance.
    # We include a set for each variable (including possibly empty ones).
    sets: List[List[int]] = []
    for var in range(1, m + 1):
        sets.append(var_to_clauses[var].copy())

    return {"universe_size": u, "sets": sets}

