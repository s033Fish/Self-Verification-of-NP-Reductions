"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) instance format is:
    {"universe_size": u, "sets": [[element, ...], ...]}
where the universe consists of the integers 0..u-1 and each inner list
represents a set (which may be empty and may appear multiple times).

The target problem (Sat) instance format is:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where variables are numbered 1..m and a literal is an integer: a positive
value +v denotes the variable v being true, a negative value -v denotes v
being false. An empty clause [] is unsatisfiable; a formula with no clauses
is trivially satisfiable.

Reduction strategy:
    * Introduce a Boolean variable x_i for each set i (1‑based indexing).
    * For every element e of the universe, let S_e be the list of set indices
      that contain e.
      - At least one set covering e must be chosen: clause (x_i1 ∨ x_i2 ∨ …).
      - No two chosen sets may both contain e: for each pair (i, j) in S_e
        add clause (¬x_i ∨ ¬x_j).
    * If an element has no covering set, the instance is a definite NO.  We
      encode this by adding an empty clause, which makes the SAT formula
      unsatisfiable.
    * Edge cases:
        - u = 0 (empty universe) is always a YES.  The reduction therefore
          returns a SAT instance with zero clauses (always satisfiable).
        - Empty sets never contribute literals to any clause; they are still
          given variables but are unrestricted, which does not affect the
          correctness of the reduction.

The reduction runs in time polynomial in the size of the Exact Cover
instance (O(u·k²) where k is the maximum number of sets containing an element).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Args:
        instance: A dictionary with keys ``"universe_size"`` (int) and
            ``"sets"`` (list of list of ints).

    Returns:
        A SAT instance dictionary with keys ``"num_vars"`` and ``"clauses"``.
    """
    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])

    m = len(sets)  # number of variables in the SAT formula
    clauses: List[List[int]] = []

    # Edge case: empty universe – always YES, return formula with no clauses.
    if u == 0:
        return {"num_vars": m, "clauses": []}

    # Pre‑compute for each element the list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            # Guard against malformed elements outside the universe; they are
            # ignored because they cannot affect coverage of valid elements.
            if 0 <= e < u:
                element_to_sets[e].append(idx)

    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element ⇒ unsatisfiable. Encode with empty clause.
            return {"num_vars": m, "clauses": [[]]}

        # At least one covering set must be chosen.
        at_least_one_clause = [idx + 1 for idx in covering]  # positive literals
        clauses.append(at_least_one_clause)

        # At most one: pairwise non‑selection.
        n = len(covering)
        for i in range(n):
            vi = covering[i] + 1
            for j in range(i + 1, n):
                vj = covering[j] + 1
                clauses.append([-vi, -vj])

    return {"num_vars": m, "clauses": clauses}

