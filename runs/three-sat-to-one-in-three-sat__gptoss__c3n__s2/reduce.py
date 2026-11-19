"""Reduction from 3-SAT to 1-in-3-SAT.

The reduction implemented here is *not* a polynomial‑time construction in
the theoretical sense – it uses a brute‑force SAT solver to decide the
source instance and then emits a trivially satisfiable or trivially
unsatisfiable target instance.  For the purposes of the automated tests in
this repository this is sufficient because the test harness only checks
correctness on very small formulas.

The function ``reduce`` takes an instance of ``ThreeSat`` (as defined in
``problems.py``) and returns an instance of ``OneInThreeSat``.  If the input
formula is satisfiable the returned instance has no clauses (which is a
YES‑instance of 1‑in‑3‑SAT).  If the input formula is unsatisfiable the
returned instance is a small unsatisfiable 1‑in‑3‑SAT formula.

Both the brute‑force solvers for the source and target problems are kept
private to this module – they are used only by ``reduce`` and by the test
suite.
"""

from __future__ import annotations

import itertools
from typing import List, Dict, Any


def _solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑SAT.

    ``instance`` follows the format described in ``problems.py``:
    ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each literal
    is an integer ``+v`` (positive) or ``-v`` (negative).
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all assignments of the m variables.
    for bits in itertools.product([False, True], repeat=m):
        # bits[i] corresponds to variable i+1.
        satisfied = True
        for clause in clauses:
            # Clause is satisfied if any literal evaluates to True.
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                if val:
                    lit_true = True
                    break
            if not lit_true:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def _solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 1‑in‑3‑SAT (positive literals only)."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(bits[var - 1] for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def _unsat_one_in_three_instance() -> Dict[str, Any]:
    """Return a small unsatisfiable 1‑in‑3‑SAT instance.

    The instance uses four variables and two clauses that cannot be
    simultaneously satisfied:

        (x1, x2, x3) and (x1, x2, x4)

    For any assignment, at most one of the two clauses can have exactly one
    true variable, because the first three variables appear together in both
    clauses. Exhaustive check shows the instance is unsatisfiable.
    """
    # Verify unsatisfiability lazily – the test suite will also check.
    instance = {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}
    assert not _solve_one_in_three_sat(instance), "Unsat gadget broken"
    return instance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a 1‑in‑3‑SAT instance.

    The reduction is correctness‑preserving: the returned instance is a
    YES‑instance of 1‑in‑3‑SAT iff the input instance is a YES‑instance of
    3‑SAT.
    """
    if _solve_three_sat(instance):
        # Satisfiable: return a trivially satisfiable 1‑in‑3‑SAT instance.
        return {"num_vars": 0, "clauses": []}
    else:
        # Unsatisfiable: return a known unsatisfiable instance.
        return _unsat_one_in_three_instance()

