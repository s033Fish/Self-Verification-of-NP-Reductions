"""Reduction from 1-in-3 SAT (positive) to Exact Cover.

The source problem (``OneInThreeSat``) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause lists three *distinct* variables (1‑based indices).

The target problem (``ExactCover``) expects instances of the form::

    {"universe_size": u, "sets": [[e1, e2, ...], ...]

with universe elements ``0 .. u‑1``.

Reduction idea
---------------
Create one universe element for every clause.  For each variable ``v`` we
form a set consisting of the indices of the clauses in which ``v`` appears.
Selecting a collection of variable‑sets that forms an exact cover means that
every clause element is covered exactly once, i.e. exactly one of the three
variables in the clause is chosen.  Interpreting the chosen variable‑sets as
the true variables yields a satisfying assignment for the 1‑in‑3‑SAT instance,
and vice‑versa.

The construction runs in time linear in the size of the input (number of
clauses plus number of variables) and therefore is polynomial.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ``OneInThreeSat`` instance to an ``ExactCover`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of variable indices, 1‑based).

    Returns
    -------
    dict
        An ``ExactCover`` instance with ``"universe_size"`` equal to the
        number of clauses and ``"sets"`` containing, for each variable ``v``
        (in order 1 .. ``num_vars``), the list of clause indices (0‑based)
        where ``v`` appears.  Variables that never appear yield an empty set –
        empty sets are harmless for Exact Cover.
    """

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Universe size is the number of clauses.
    universe_size = len(clauses)

    # Prepare a list for each variable to collect clause indices.
    var_to_clauses: List[List[int]] = [[] for _ in range(num_vars)]

    for idx, clause in enumerate(clauses):
        # Each clause is guaranteed to have exactly three distinct variables.
        for var in clause:
            # Convert 1‑based variable index to 0‑based list position.
            var_to_clauses[var - 1].append(idx)

    # The Exact Cover instance.
    exact_cover_instance = {
        "universe_size": universe_size,
        "sets": var_to_clauses,
    }
    return exact_cover_instance

