"""Reduction from 3‑SAT to Exact Cover.

The source problem (ThreeSat) instance format is::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (meaning variable ``v`` is
true) or ``-v`` (meaning variable ``v`` is false).  Variables are numbered
starting at ``1``.

The target problem (ExactCover) instance format is::

    {"universe_size": u, "sets": [[e1, e2, ...], ...]}

The reduction follows the classic construction used in Knuth's *Algorithm
X*:

* The universe consists of one element for each variable (to enforce a
  consistent truth assignment) and one element for each clause (to enforce
  that every clause is satisfied exactly once).
* For each variable we create two sets: one representing assigning the
  variable True and one representing assigning it False.  The set for a
  truth value contains the variable element and all clause elements that are
  satisfied by the corresponding literal.  If a literal never appears, the
  set is just the singleton containing the variable element.
* Selecting exactly one of the two sets for each variable yields a truth
  assignment.  Because each clause element appears in at most one of the
  chosen sets, the clauses are covered exactly once iff the assignment
  satisfies every clause.

The construction runs in time linear in the size of the 3‑SAT instance,
which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        3‑element lists of integers representing literals).

    Returns
    -------
    dict
        Exact Cover instance with keys ``"universe_size"`` and ``"sets"``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Universe: first m elements are variables, next c elements are clauses.
    universe_size = m + c
    sets: List[List[int]] = []

    # Record which clause element each literal can satisfy.
    pos_clauses: List[List[int]] = [[] for _ in range(m)]  # +v appears in these clause elements
    neg_clauses: List[List[int]] = [[] for _ in range(m)]  # -v appears in these clause elements

    for clause_idx, clause in enumerate(clauses):
        clause_elem = m + clause_idx
        for lit in clause:
            var = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                pos_clauses[var].append(clause_elem)
            else:
                neg_clauses[var].append(clause_elem)

    # For each variable create two sets: one for True, one for False.
    for var in range(m):
        true_set = [var] + pos_clauses[var]
        false_set = [var] + neg_clauses[var]
        sets.append(true_set)
        sets.append(false_set)

    return {"universe_size": universe_size, "sets": sets}

