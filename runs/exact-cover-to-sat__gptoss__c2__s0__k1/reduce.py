"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined as:
    instance = {"universe_size": u, "sets": [[element, ...], ...]}
    Elements are integers 0..u-1.  We ask whether we can pick a sub‑collection
    of the given sets such that they are pairwise disjoint and their union is
    the whole universe.

The target problem (Sat) expects a CNF formula:
    instance = {"num_vars": m, "clauses": [[literal, ...], ...]}
    Literals are signed integers: +v (v true) or -v (v false).  An empty clause
    [] is unsatisfiable, a formula with no clauses is trivially satisfiable.

We construct a SAT formula that is satisfiable iff the exact‑cover instance
has a solution.

Construction:
    * Introduce a Boolean variable x_i for each set i (1‑based indexing as
      required by the SAT format).
    * For every element e in the universe we collect the indices of sets that
      contain e, say I_e.
        - At least one of those sets must be chosen: clause (x_i for i in I_e).
        - At most one of them may be chosen: for every pair i<j in I_e add the
          clause (¬x_i ∨ ¬x_j).
    * If an element e is not contained in any set, the exact‑cover instance is
      a definite NO.  We return a formula that is unsatisfiable – a single
      empty clause suffices.
    * The case u = 0 is a YES (choose no sets).  Any SAT instance with zero
      clauses is satisfiable, so we return an empty formula.

The reduction runs in polynomial time: we examine each set once and, for each
element, possibly add O(k^2) clauses where k is the number of sets containing
that element.  Since the total size of the input bounds the sum of those k's,
the overall work is O(|sets| * max_k) ≤ polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "universe_size" (int) and "sets" (list of
        list of ints) following the specification of ``ExactCover``.

    Returns
    -------
    dict
        A SAT instance in the format required by ``Sat``.
    """

    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])
    n_sets: int = len(sets)

    # Edge case: empty universe – always YES.
    if u == 0:
        return {"num_vars": n_sets, "clauses": []}

    # Build a mapping from element to list of set indices (0‑based).
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            if 0 <= e < u:
                element_to_sets[e].append(idx)
            else:
                # Elements outside the universe can be ignored – they never
                # affect the covering condition.
                pass

    clauses: List[List[int]] = []

    # Check each element for coverage constraints.
    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element → unsatisfiable.
            return {"num_vars": n_sets, "clauses": [[]]}

        # At least one covering set must be chosen.
        at_least_one = [idx + 1 for idx in covering]  # positive literals
        clauses.append(at_least_one)

        # At most one covering set: pairwise negative clauses.
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                clauses.append([-(covering[i] + 1), -(covering[j] + 1)])

    return {"num_vars": n_sets, "clauses": clauses}

