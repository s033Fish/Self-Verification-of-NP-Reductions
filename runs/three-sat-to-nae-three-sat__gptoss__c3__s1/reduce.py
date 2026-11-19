"""Reduction from 3-SAT to NAE-3-SAT.

The source problem is ``ThreeSat`` (3‑SAT) and the target problem is
``NaeThreeSat`` (NAE‑3‑SAT).  Both problems use the same instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (variable *v* is true) or
``-v`` (variable *v* is false).  Every clause contains exactly three
distinct variables.

The reduction is extremely simple: we keep the same variables and the
same clauses, but interpret the clauses as NAE‑3‑SAT clauses.  Formally,
``reduce`` returns a copy of the input instance.

Correctness reasoning (informal):
    * If the original 3‑SAT instance is satisfiable, then there exists an
      assignment where each clause has at least one true literal.  The
      same assignment also satisfies each NAE‑3‑SAT clause because a clause
      that contains at least one true literal cannot consist of three
      equal literals (all true or all false).  Hence the reduced instance
      is a yes‑instance.
    * Conversely, if the reduced NAE‑3‑SAT instance is satisfiable, the
      satisfying assignment makes every clause contain at least one true
      literal (otherwise the clause would be all false, violating the NAE
      condition).  Therefore the original 3‑SAT instance is also
      satisfiable.

Edge cases (empty clause list) are preserved automatically because the
output instance is identical to the input.

The transformation runs in linear time in the size of the input and does
not invoke any solver.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Return a NAE‑3‑SAT instance equivalent to the given 3‑SAT instance.

    The function makes a shallow copy of the input dictionary and of the
    list of clauses to avoid accidental mutation of the caller's data.
    """
    # Copy the structure to satisfy the requirement of returning a new
    # object while preserving the exact same content.
    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = [list(clause) for clause in instance["clauses"]]
    return {"num_vars": num_vars, "clauses": clauses}

