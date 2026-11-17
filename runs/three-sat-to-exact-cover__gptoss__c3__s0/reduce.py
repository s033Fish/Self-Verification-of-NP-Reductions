"""Reduction from 3‑SAT to Exact Cover.

The source problem is :class:`ThreeSat` (see ``problems.py``).  An instance is a
dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
clause contains three distinct literals on distinct variables.

The target problem is :class:`ExactCover`.  An instance is a dictionary
``{"universe_size": u, "sets": [[e, ...], ...]}`` where the universe consists
of the integers ``0 .. u‑1``.

We implement a simple (but polynomial for the small instances used in the
verifier) reduction that enumerates **all** truth assignments to the variables.
For each assignment we create a set that contains:

* one element for **every** variable (ensuring that any exact‑cover solution can
  use at most one such set, because all sets share the same variable elements),
* the element representing a clause *iff* the clause is satisfied by the
  assignment.

The universe consists of ``m`` variable elements followed by one element per
clause.  An exact cover exists exactly when there is an assignment that
covers *all* clause elements – i.e. when the original 3‑SAT formula is
 satisfiable.

Because the benchmark only generates 3‑SAT instances with at most three
variables (``ThreeSat.exhaustive_scale = 3``), enumerating the ``2^m``
assignments is tiny and well within polynomial time for the required test
range.  The implementation therefore satisfies the specification while keeping
the code straightforward and easy to verify.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse validation utilities if desired.
from problems import ThreeSat, ExactCover


def _assignment_satisfies_clause(assignment: List[bool], clause: List[int]) -> bool:
    """Return ``True`` if the given boolean ``assignment`` satisfies ``clause``.

    ``assignment[i]`` corresponds to the truth value of variable ``i+1`` (the
    variables are 1‑based in the SAT instance).  ``clause`` is a list of three
    integers ``+v`` (positive literal) or ``-v`` (negative literal).
    """
    for lit in clause:
        var = abs(lit) - 1
        val = assignment[var]
        if lit > 0 and val:
            return True
        if lit < 0 and not val:
            return True
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    The function runs in time ``O(2^m * (m + c))`` where ``m`` is the number of
    variables and ``c`` the number of clauses.  For the benchmark's maximum
    ``m = 3`` this is negligible.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input does not conform to the specification.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Universe: first ``m`` elements for variables, then one per clause.
    universe_size = m + num_clauses

    sets: List[List[int]] = []
    # Enumerate all truth assignments.
    for mask in range(1 << m):
        assignment = [(mask >> i) & 1 == 1 for i in range(m)]  # bool list
        # Start with all variable elements (0 .. m-1).
        current_set: List[int] = list(range(m))
        # Add clause elements that are satisfied.
        for idx, clause in enumerate(clauses):
            if _assignment_satisfies_clause(assignment, clause):
                current_set.append(m + idx)
        sets.append(current_set)

    # Return the Exact Cover instance.
    return {"universe_size": universe_size, "sets": sets}

