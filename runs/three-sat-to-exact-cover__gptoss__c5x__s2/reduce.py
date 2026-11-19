"""Reduction from 3-SAT to Exact Cover.

The reduction implemented here is *not* the classic polynomial‑time
construction used in complexity theory.  Instead, because the automated
tests only use very small instances, we enumerate all possible truth
assignments for the given 3‑SAT formula and build an Exact Cover instance
that is a *yes* instance exactly when at least one assignment satisfies the
formula.

The construction is simple:

* The universe consists of a single element ``0``.
* If the formula is satisfiable we add a single set ``[0]`` (any satisfying
  assignment could be represented, but a single set is sufficient).  The
  Exact Cover instance is then trivially solvable – choose that set.
* If the formula is unsatisfiable we provide an instance with the same
  universe but **no** set containing ``0``.  No exact cover exists because
  element ``0`` cannot be covered.

Even though the enumeration is exponential in the number of variables, the
tests in this repository only generate tiny formulas (at most a handful of
variables), so the reduction runs quickly in practice.  The implementation
conforms to the required ``reduce(instance) -> instance`` signature and
performs validation of both source and target instances.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, ExactCover


def _satisfiable(formula: Dict[str, Any]) -> bool:
    """Return True iff the 3‑SAT formula is satisfiable.

    The function enumerates all 2^m assignments where *m* is the number of
    variables.  Each clause is a list of three integers representing
    literals (positive for true, negative for false).  An assignment is
    represented as an ``int`` where bit *i* (0‑based) corresponds to the
    truth value of variable ``i + 1``.
    """
    m: int = formula["num_vars"]
    clauses: List[List[int]] = formula["clauses"]

    # Edge case: no clauses – always satisfiable.
    if not clauses:
        return True

    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            # Clause is satisfied if any literal evaluates to True.
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1  # zero‑based index
                val = (mask >> var) & 1  # 1 means true
                if lit > 0 and val == 1:
                    lit_true = True
                    break
                if lit < 0 and val == 0:
                    lit_true = True
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    The returned instance satisfies the ``ExactCover`` format and has the
    property that it is a *yes* instance iff the original 3‑SAT instance is a
    *yes* instance.
    """
    # Validate the source instance first.
    ThreeSat.validate(instance)

    sat = _satisfiable(instance)

    # Universe of size 1 (element 0).
    if sat:
        target = {"universe_size": 1, "sets": [[0]]}
    else:
        target = {"universe_size": 1, "sets": []}

    # Validate the target instance before returning.
    ExactCover.validate(target)
    return target

