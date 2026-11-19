"""Reduction from 1-in-3-SAT (positive literals only) to 3-SAT.

The source problem is defined in ``problems.OneInThreeSat`` and expects
instances of the form ``{"num_vars": m, "clauses": [[a, b, c], ...]}`` where
``a, b, c`` are positive integers representing variables.  An assignment is a
yes‑instance iff **exactly one** variable in each clause is true.

The target problem is ``problems.ThreeSat`` whose clauses are 3‑CNF literals
with possible negations.  An assignment is a yes‑instance iff every clause
contains at least one true literal.

To enforce the *exactly‑one* condition for a clause (a, b, c) we add the
following five 3‑SAT clauses, each of which is falsified only by one of the
forbidden assignments:

* ( a ∨  b ∨  c)   – blocks the all‑false assignment.
* (¬a ∨ ¬b ∨ ¬c)   – blocks the all‑true assignment.
* (¬a ∨ ¬b ∨  c)   – blocks a=1, b=1, c=0.
* (¬a ∨  b ∨ ¬c)   – blocks a=1, b=0, c=1.
* ( a ∨ ¬b ∨ ¬c)   – blocks a=0, b=1, c=1.

These clauses use only the original variables, contain exactly three literals on
three distinct variables, and together are equivalent to the exactly‑one
requirement.  The reduction keeps the same number of variables and replaces each
source clause with the five clauses above.
"""

from __future__ import annotations

from typing import Dict, List

import problems


def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3‑SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of ``OneInThreeSat``.

    Returns
    -------
    dict
        A dictionary adhering to the format of ``ThreeSat`` such that the
        original instance is satisfiable **iff** the returned instance is.
    """
    # Validate the source instance first – this will raise if malformed.
    problems.OneInThreeSat.validate(instance)

    num_vars = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    target_clauses: List[List[int]] = []
    for clause in source_clauses:
        a, b, c = clause
        # exactly‑one constraints encoded as five 3‑SAT clauses
        target_clauses.append([a, b, c])          # at least one true
        target_clauses.append([-a, -b, -c])       # at most one true (all true forbidden)
        target_clauses.append([-a, -b, c])        # forbid a=1,b=1,c=0
        target_clauses.append([-a, b, -c])        # forbid a=1,b=0,c=1
        target_clauses.append([a, -b, -c])        # forbid a=0,b=1,c=1

    reduced_instance = {"num_vars": num_vars, "clauses": target_clauses}
    # Validate the produced target instance for safety.
    problems.ThreeSat.validate(reduced_instance)
    return reduced_instance

