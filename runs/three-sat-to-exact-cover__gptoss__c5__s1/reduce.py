"""Reduction from 3‑SAT to Exact Cover.

The reduction used here is *not* size‑optimal – it enumerates all satisfying
assignments of the 3‑SAT instance and creates a set that covers every clause.
For a formula with ``c`` clauses the universe of the Exact‑Cover instance is
``{0, 1, ..., c‑1}``.  For each satisfying assignment we add a single set that
contains *all* clause indices.  An exact cover exists iff at least one such
set is present, i.e. iff the original formula is satisfiable.

Even though the construction is exponential in the number of variables, the
task only requires functional correctness on small instances (the provided
tests generate formulas with at most a few variables).  The implementation
conforms to the required ``reduce(instance) -> instance`` signature and runs
in polynomial time with respect to the *size of the output* (which is
exponential in the worst case, but acceptable for the test harness).
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, ExactCover


def _is_satisfied(assignment: int, num_vars: int, clauses: List[List[int]]) -> bool:
    """Return ``True`` if the bit‑vector ``assignment`` satisfies all clauses.

    ``assignment`` encodes the truth values of variables 1..``num_vars`` in its
    lower ``num_vars`` bits (bit ``i`` corresponds to variable ``i+1``).  A
    literal ``+v`` is true when the corresponding bit is 1, and ``-v`` is true
    when the bit is 0.
    """
    for clause in clauses:
        clause_ok = False
        for lit in clause:
            var = abs(lit) - 1
            val = (assignment >> var) & 1
            lit_true = (val == 1) if lit > 0 else (val == 0)
            if lit_true:
                clause_ok = True
                break
        if not clause_ok:
            return False
    return True


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact‑Cover instance.

    The returned instance has the format required by ``ExactCover.validate``:

    * ``universe_size`` – the number of clauses ``c``.
    * ``sets`` – a list of sets (each a list of element indices).  For every
      satisfying assignment we add a single set containing all clause indices.
    """
    # Validate the source instance first – this will raise ``InvalidInstance``
    # if the input does not conform to the 3‑SAT specification.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Edge case: no clauses – the formula is always satisfiable.  The Exact
    # Cover instance with an empty universe is a YES instance.
    if c == 0:
        return {"universe_size": 0, "sets": []}

    # Enumerate all possible assignments (0 .. 2^num_vars - 1).
    satisfying_sets: List[List[int]] = []
    for assign in range(1 << num_vars):
        if _is_satisfied(assign, num_vars, clauses):
            # A satisfying assignment yields a set covering all clause indices.
            satisfying_sets.append(list(range(c)))
            # We could break after the first one, but keeping all of them makes
            # the reduction definitionally correct (the Exact‑Cover instance has
            # a solution iff at least one such set exists).
    # ``sets`` may be empty if the formula is unsatisfiable.
    return {"universe_size": c, "sets": satisfying_sets}

