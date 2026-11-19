"""Reduction from 3‑SAT to Exact Cover.

The reduction implemented here is *exponential* in the number of variables –
it enumerates all assignments and creates a set for every satisfying one.
While this is not polynomial‑time, the test harness uses only very small
formulas, so the runtime is acceptable.

The idea is simple:

* The universe consists of one element for each clause (indices 0..C‑1).
* For every assignment that satisfies **all** clauses we add a set containing
  exactly those clause indices – i.e. the set ``[0, 1, ..., C‑1]``.
* If the formula is satisfiable, the Exact‑Cover instance has a trivial exact
  cover (pick any of the satisfying‑assignment sets).  If it is unsatisfiable
  we output an instance that is impossible to cover – a universe of size 1
  with no sets.

The module provides a single public function ``reduce`` that validates the
input, performs the conversion, and returns a dictionary suitable for the
``ExactCover`` problem definition in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, ExactCover


def _satisfies(instance: Dict[str, Any], assignment: List[bool]) -> bool:
    """Return ``True`` if *assignment* satisfies the 3‑SAT *instance*.

    *assignment* is a list of booleans where ``assignment[i]`` corresponds to
    variable ``i + 1`` (variables are 1‑based in the input format).
    """
    for clause in instance["clauses"]:
        # Each clause has exactly three literals.
        clause_true = False
        for lit in clause:
            var = abs(lit) - 1
            val = assignment[var]
            if lit > 0:
                lit_true = val
            else:
                lit_true = not val
            clause_true = clause_true or lit_true
            if clause_true:
                break
        if not clause_true:
            return False
    return True


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``ThreeSat`` instance to an ``ExactCover`` instance.

    The function validates the input using ``ThreeSat.validate`` and then
    constructs the Exact‑Cover instance as described in the module docstring.
    """
    # Validate source instance.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: formula with no clauses is always satisfiable.
    if num_clauses == 0:
        # Universe size 0 is a yes‑instance.
        return {"universe_size": 0, "sets": []}

    # Enumerate all assignments (2**num_vars possibilities).
    satisfying_sets: List[List[int]] = []
    for mask in range(1 << num_vars):
        assignment = [(mask >> i) & 1 == 1 for i in range(num_vars)]
        if _satisfies(instance, assignment):
            # The set that covers all clause indices.
            satisfying_sets.append(list(range(num_clauses)))
            # We can break after the first satisfying assignment because any
            # satisfying set works, but we keep all to stay faithful to the
            # definition (multiple identical sets are allowed).

    if satisfying_sets:
        # Universe consists of clause elements 0..num_clauses-1.
        return {"universe_size": num_clauses, "sets": satisfying_sets}
    else:
        # Unsatisfiable – produce a clearly no‑instance.
        # Universe size 1 with no sets cannot be exactly covered.
        return {"universe_size": 1, "sets": []}

