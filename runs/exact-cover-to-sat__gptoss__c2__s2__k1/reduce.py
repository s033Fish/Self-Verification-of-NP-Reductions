"""Reduction from Exact Cover to SAT.

The source problem (ExactCover) is defined by a universe of size ``u`` and a
list of subsets of that universe.  The task is to decide whether there exists a
subfamily of the given sets that partitions the universe – i.e., each element
appears in exactly one chosen set.

We produce a CNF formula (SAT) that is satisfiable exactly when such a family
exists.  The construction is classic:

* Introduce a Boolean variable ``x_i`` for each input set ``i`` (1‑based indexing
  as required by the SAT format).  Setting ``x_i`` to true means that the set is
  selected.
* For every element ``e`` of the universe we add two kinds of constraints:

  1. **Coverage** – at least one of the sets containing ``e`` must be chosen.
     This is a single clause ``(x_{i1} ∨ x_{i2} ∨ …)`` where the indices are the
     sets that contain ``e``.
  2. **Uniqueness** – no two chosen sets may both contain ``e``.  For each pair
     of distinct sets ``i`` and ``j`` that both contain ``e`` we add the clause
     ``(¬x_i ∨ ¬x_j)``.

If an element does not appear in any set we add the empty clause ``[]`` which
is unsatisfiable, correctly reflecting that the Exact Cover instance is a
"no".

Edge cases are handled automatically:

* ``u = 0`` – the loop over elements produces no clauses, yielding a formula
  with zero clauses, which is trivially satisfiable.
* Empty input sets never appear in any element clause, so their variables are
  free – they do not affect satisfiability, matching the semantics of Exact
  Cover where empty sets are irrelevant.
* Duplicate non‑empty sets lead to pairwise ``(¬x_i ∨ ¬x_j)`` constraints for
  each shared element, preventing both from being selected.

The reduction runs in time polynomial in the size of the Exact Cover instance
(``O(u·k²)`` where ``k`` is the maximum number of sets containing a single
element), which satisfies the required complexity bound.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list of
        lists of ints) as described in ``problems.py``.

    Returns
    -------
    dict
        A SAT instance in the format ``{"num_vars": m, "clauses": [...]}``.
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n: int = len(sets)  # number of variables in the SAT formula

    # Map each element to the list of variable indices (1‑based) of sets that
    # contain it.
    element_to_vars: Dict[int, List[int]] = {e: [] for e in range(u)}
    for idx, s in enumerate(sets, start=1):  # SAT variables are 1‑based
        for e in s:
            # The problem guarantees elements are in 0..u-1, but we guard
            # against malformed input just in case.
            if 0 <= e < u:
                element_to_vars[e].append(idx)

    clauses: List[List[int]] = []

    # For each element, enforce "exactly one" selection among the covering
    # sets using the standard CNF encoding.
    for e in range(u):
        vars_with_e = element_to_vars[e]
        if not vars_with_e:
            # No set covers this element -> unsatisfiable clause.
            clauses.append([])
            continue

        # At least one covering set is chosen.
        clauses.append(vars_with_e.copy())

        # At most one: for every unordered pair add a clause forbidding both.
        for i in range(len(vars_with_e)):
            vi = vars_with_e[i]
            for j in range(i + 1, len(vars_with_e)):
                vj = vars_with_e[j]
                clauses.append([-vi, -vj])

    return {"num_vars": n, "clauses": clauses}

