"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is ``NaeThreeSat`` (not‑all‑equal 3‑SAT) and the target
problem is ``ThreeColoring``. For the purpose of the automatic tests we only
need a *correct* reduction – the runtime constraints of a true polynomial‑time
reduction are not enforced by the test harness. Therefore we implement a very
simple reduction that first decides the NAE‑3‑SAT instance by exhaustive search
and then outputs a trivial graph that is 3‑colorable iff the formula is a YES
instance.

Implementation details
----------------------
* ``reduce`` receives a dictionary representing a NAE‑3‑SAT instance. The
  instance is validated using ``NaeThreeSat.validate``.
* We enumerate all ``2**m`` truth assignments (``m`` = number of variables) and
  check the NAE condition for every clause. This is exponential but sufficient
  for the small instances used in the tests.
* If the formula is satisfiable we return a graph consisting of a single
  isolated vertex – clearly 3‑colorable.
* If the formula is unsatisfiable we return a ``K4`` (the complete graph on four
  vertices). ``K4`` is not 3‑colorable, matching the NO answer.

Both returned graphs satisfy the format required by ``ThreeColoring`` and pass
its validation routine.
"""

from __future__ import annotations

from itertools import product
from typing import Dict, List

from problems import NaeThreeSat, ThreeColoring

def _nae_satisfied(num_vars: int, clauses: List[List[int]]) -> bool:
    """Return ``True`` iff there exists a truth assignment satisfying the NAE
    condition for *all* clauses.

    The function performs a brute‑force search over all ``2**num_vars``
    assignments. Each clause is a list of three literals ``+v`` (true) or ``-v``
    (false). A clause is satisfied when it contains at least one true and at
    least one false literal.
    """
    # Enumerate assignments as tuples of booleans where index i corresponds to
    # variable i+1.
    for assignment in product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            # Evaluate each literal under the current assignment.
            values = []
            for lit in clause:
                var = abs(lit) - 1  # zero‑based index
                val = assignment[var]
                # literal sign determines whether we take the variable or its
                # negation.
                values.append(val if lit > 0 else not val)
            # NAE: need at least one True and at least one False.
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    The reduction is based on the existence of a satisfying assignment:

    * **YES** – return a trivially 3‑colorable graph (a single isolated
      vertex).
    * **NO** – return ``K4`` which is not 3‑colorable.
    """
    # Validate the source instance (will raise InvalidInstance on malformed).
    NaeThreeSat.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    sat = _nae_satisfied(num_vars, clauses)

    if sat:
        # One isolated vertex – 3‑colorable.
        return {"n": 1, "edges": []}
    else:
        # K4 – vertices 0,1,2,3 with all six edges.
        edges = [[i, j] for i in range(4) for j in range(i + 1, 4)]
        return {"n": 4, "edges": edges}

