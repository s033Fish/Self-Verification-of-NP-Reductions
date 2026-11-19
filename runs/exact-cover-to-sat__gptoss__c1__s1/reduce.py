"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined by a dictionary with keys:

    {
        "universe_size": u,          # number of elements 0..u-1
        "sets": [[e1, e2, ...], ...] # list of sets, each a list of distinct elements
    }

The target problem (Sat) expects a dictionary in conjunctive‑normal‑form:

    {
        "num_vars": m,               # variables are 1..m
        "clauses": [[lit, ...], ...] # each clause is a list of integer literals
    }

Literal encoding follows the convention used in ``problems.py``:
    +v  →  v   (positive integer)
    -v  → -v   (negative integer)

The reduction introduces a boolean variable x_i for each set i (0‑based index).
Variable numbers in the SAT instance are therefore i+1.

Constraints:
  * For every element e of the universe, at least one chosen set must contain e.
    This is encoded as a clause (x_i1 ∨ x_i2 ∨ …) where the i_k are the indices of
    sets that contain e.
  * No two chosen sets may share an element.  For each pair of sets that both
    contain the same element we add a clause (¬x_i ∨ ¬x_j).
If an element is not covered by any set we add an empty clause ``[]`` which makes
the formula unsatisfiable, matching the fact that the Exact Cover instance is a
"no" instance.

Edge cases handled explicitly:
  * Universe size 0 – the exact‑cover instance is trivially a "yes".  We return a
    SAT instance with 0 variables and no clauses, which is satisfiable.
  * Empty sets are simply ignored by the construction because they contribute
    no literals to any clause; they may be assigned arbitrarily, which is fine
    because adding an empty set to a cover does not affect disjointness or
    coverage.

The function runs in time polynomial in the size of the input (O(u·n²) in the
worst case, which is acceptable for a polynomial‑time reduction).
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        Exact Cover instance with keys ``"universe_size"`` and ``"sets"``.

    Returns
    -------
    dict
        SAT instance with keys ``"num_vars"`` and ``"clauses"``.
    """

    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])
    n: int = len(sets)

    # Trivial yes case: empty universe – return a trivially satisfiable formula.
    if u == 0:
        return {"num_vars": 0, "clauses": []}

    # Build a mapping from each element to the list of set indices containing it.
    element_to_sets: Dict[int, List[int]] = {e: [] for e in range(u)}
    for idx, s in enumerate(sets):
        for e in s:
            # Elements are guaranteed to be in 0..u-1 by the problem statement.
            if 0 <= e < u:
                element_to_sets[e].append(idx)
            else:
                # Out‑of‑range elements can be ignored; they will never be needed
                # for covering the universe.
                continue

    clauses: List[List[int]] = []

    # For each element enforce "exactly one" covering set.
    for e in range(u):
        covering = element_to_sets.get(e, [])
        if not covering:
            # No set covers this element → unsatisfiable.  Add an empty clause.
            clauses.append([])
            continue

        # At least one covering set must be chosen.
        clauses.append([idx + 1 for idx in covering])

        # At most one: for every pair, add a clause (¬x_i ∨ ¬x_j).
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                clauses.append([-(covering[i] + 1), -(covering[j] + 1)])

    return {"num_vars": n, "clauses": clauses}


__all__ = ["reduce"]
