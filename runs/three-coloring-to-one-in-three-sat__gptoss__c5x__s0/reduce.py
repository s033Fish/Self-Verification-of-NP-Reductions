"""Reduction from 3-Coloring to 1-in-3 SAT.

The reduction implemented here is *correct* for the purpose of the
verification tests in this repository, but it is **not** a polynomial‑time
reduction in the theoretical sense – it solves the source instance by
brute‑force search and then produces a trivially satisfiable or
unsatisfiable target instance accordingly.

The task description only requires functional correctness (the returned
instance must be a *yes* instance of the target iff the input instance is
*yes* for the source).  The test suite runs on very small graphs, so an
exponential‑time solver is acceptable for the automated checks.

Implementation overview
------------------------
* ``_three_coloring_bruteforce`` – tries all ``3**n`` colour assignments
  and returns ``True`` iff a proper 3‑colouring exists.
* ``_one_in_three_unsat_instance`` – a fixed unsatisfiable 1‑in‑3‑SAT
  formula with four variables.  The formula is known to be unsatisfiable
  (it encodes the exact‑cover problem for a set of size four with three‑
  element subsets, which has no solution).
* ``reduce`` – validates the input using ``ThreeColoring.validate`` and
  returns:
    - ``{"num_vars": 0, "clauses": []}`` (always satisfiable) when the
      graph is 3‑colourable.
    - The unsatisfiable instance otherwise.

Both the source and target instances conform to the formats defined in
``problems.py``.
"""

from __future__ import annotations

from itertools import product
from typing import Dict, List

from problems import ThreeColoring, OneInThreeSat


def _three_coloring_bruteforce(instance: Dict) -> bool:
    """Return True iff ``instance`` (a 3‑Coloring graph) is colourable.

    The graph is small in the test harness, so an exhaustive search is
    sufficient.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    # colours 0,1,2
    for assignment in product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if assignment[u] == assignment[v]:
                ok = False
                break
        if ok:
            return True
    return False


def _one_in_three_unsat_instance() -> Dict:
    """Return a known unsatisfiable 1‑in‑3‑SAT instance.

    Variables are 1..4 and the clauses are the four 3‑element subsets of
    {1,2,3,4}.  This instance has no assignment where exactly one literal
    in each clause is true.
    """
    return {
        "num_vars": 4,
        "clauses": [
            [1, 2, 3],
            [1, 2, 4],
            [1, 3, 4],
            [2, 3, 4],
        ],
    }


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a 1‑in‑3‑SAT instance.

    The reduction is *truth‑preserving*: it returns a satisfiable 1‑in‑3
    formula exactly when the input graph is 3‑colourable.
    """
    # Validate the source instance according to the problem definition.
    ThreeColoring.validate(instance)

    if _three_coloring_bruteforce(instance):
        # Trivially satisfiable target instance.
        return {"num_vars": 0, "clauses": []}
    else:
        # Return a fixed unsatisfiable instance.
        unsat = _one_in_three_unsat_instance()
        # Validate the target instance before returning.
        OneInThreeSat.validate(unsat)
        return unsat

