"""Reduction from Exact Cover to SAT.

The reduction follows the classic textbook construction:

* For each set S_i in the exact‑cover instance we create a Boolean variable
  x_i (represented by variable index i+1 in the SAT instance).
* For every element e of the universe we add two kinds of constraints:
  - **At least one** of the sets that contain e must be chosen.  This is
    encoded as a clause (x_i1 ∨ x_i2 ∨ …) where each i_j is a set that
    contains e.
  - **At most one** of those sets may be chosen.  For every pair of distinct
    sets i < j that both contain e we add the clause (¬x_i ∨ ¬x_j).

If an element has no covering set we add an empty clause – by definition an
empty clause is unsatisfiable, which correctly reflects that the exact‑cover
instance has no solution.

Edge cases:
* ``universe_size == 0`` – the exact‑cover instance is trivially a YES
  instance.  We return a SAT instance with ``num_vars = 0`` and no clauses;
  such a formula is satisfiable.
* Empty sets never participate in any clause because they contain no
  elements.  Their corresponding variables are therefore free, which is fine –
  a satisfying assignment can simply set them to false.

The function runs in time polynomial in the size of the input (O(u·k^2) in
the worst case, where ``k`` is the number of sets).
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ExactCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SAT instance.

    Args:
        instance: A dictionary adhering to the ExactCover format.

    Returns:
        A dictionary adhering to the Sat format such that the SAT instance
        is satisfiable iff the original ExactCover instance has an exact
        cover.
    """
    # Validate the input according to the ExactCover definition.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    k = len(sets)

    # Trivial YES case: empty universe – any assignment works, we can return
    # an empty formula (which is satisfiable).
    if u == 0:
        return {"num_vars": k, "clauses": []}

    # Build a mapping from element to list of set indices that contain it.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            element_to_sets[e].append(idx)

    clauses: List[List[int]] = []

    for e in range(u):
        covering = element_to_sets[e]
        if not covering:
            # No set covers this element – unsatisfiable. Represented by an
            # empty clause.
            clauses.append([])
            continue
        # At least one covering set must be chosen.
        at_least_one = [idx + 1 for idx in covering]  # SAT variables are 1‑based
        clauses.append(at_least_one)
        # At most one: for each pair, add a clause (¬i ∨ ¬j).
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                vi = -(covering[i] + 1)
                vj = -(covering[j] + 1)
                clauses.append([vi, vj])

    return {"num_vars": k, "clauses": clauses}

