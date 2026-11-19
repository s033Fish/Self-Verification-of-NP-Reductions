"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined as::

    Instance: {"universe_size": u, "sets": [[element, ...], ...]}
    Yes iff there exists a sub‑collection of the given sets that are
    pairwise disjoint and whose union is the whole universe {0,…,u‑1}.

The target problem (Sat) expects an instance of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where literals are signed integers: +v means variable *v* is true and
‑v means variable *v* is false (variables are 1‑based).

The classic polynomial‑time reduction introduces a Boolean variable
``x_i`` for each set *i* (whether the set is selected).  For every element
``e`` in the universe we enforce two constraints:

1. **At least one** of the sets containing ``e`` must be chosen.
2. **At most one** of those sets may be chosen (pairwise mutual exclusion).

If an element is not present in any set, the Exact Cover instance is a
*no*‑instance.  To reflect this we add an empty clause (``[]``) which is
unsatisfiable in SAT.

Edge cases:
* ``u = 0`` – the empty universe is always exactly covered.  The reduction
  therefore returns a SAT instance with *no* clauses, which is trivially
  satisfiable.
* Empty sets never contribute literals to any element clause, so they are
  unrestricted in the SAT formula – matching the fact that they are
  irrelevant for Exact Cover.

The function runs in time polynomial in the size of the input (``O(u·k²)``
where ``k`` is the maximum number of sets containing a single element).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"``
        (list of list of ints).

    Returns
    -------
    dict
        A SAT instance in the required format.
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m: int = len(sets)  # number of variables

    # List of clauses to be built.
    clauses: List[List[int]] = []

    # Edge case: empty universe – always satisfiable, return formula with
    # no clauses.
    if u == 0:
        return {"num_vars": m, "clauses": []}

    # For each element, gather indices of sets that contain it.
    for element in range(u):
        containing: List[int] = []
        for idx, s in enumerate(sets):
            # ``s`` may be large; a simple ``in`` check is fine for the
            # expected input sizes.
            if element in s:
                containing.append(idx)

        if not containing:
            # No set covers this element → unsatisfiable.  Adding an empty
            # clause makes the whole formula unsatisfiable.
            clauses.append([])
            # No need to add other constraints for this element.
            continue

        # At‑least‑one clause: all variables corresponding to covering sets
        # are positive literals.
        at_least_one = [i + 1 for i in containing]  # SAT variables are 1‑based
        clauses.append(at_least_one)

        # At‑most‑one constraints: for each unordered pair, add a clause
        # (¬xi ∨ ¬xj).
        n = len(containing)
        for i in range(n):
            vi = containing[i] + 1
            for j in range(i + 1, n):
                vj = containing[j] + 1
                clauses.append([-vi, -vj])

    return {"num_vars": m, "clauses": clauses}
