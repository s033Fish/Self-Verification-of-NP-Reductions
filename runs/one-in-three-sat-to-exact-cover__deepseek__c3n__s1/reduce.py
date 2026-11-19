"""Polynomial-time reduction from 1-in-3-SAT (OneInThreeSat) to Exact Cover.

Key observation
---------------
1-in-3-SAT asks for a global truth assignment such that every clause contains
EXACTLY ONE true variable.  Think of the clauses as the universe and, for each
variable v, of the set S_v = { clauses that contain v }.

Choosing a collection of variables to be TRUE, the corresponding sets S_v are
pairwise disjoint exactly when no clause contains two chosen variables, and
their union is the whole universe exactly when every clause contains at least
one chosen variable.  Together these say every clause contains exactly one
chosen (true) variable -- precisely the 1-in-3-SAT condition.

So the Exact Cover instance

    universe_size = number of clauses
    sets          = [ S_v for v in 1..num_vars ]

is a yes-instance iff the 1-in-3-SAT instance is satisfiable.

Edge cases:
  * No clauses  -> universe_size = 0 -> Exact Cover is yes (choose nothing),
    matching the fact that a clause-free formula is yes.
  * Variables that occur in no clause produce empty sets; empty sets are
    allowed and never matter.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    num_clauses = len(clauses)

    # sets[v-1] = sorted list of clause indices containing variable v.
    sets: list[list[int]] = [[] for _ in range(num_vars)]
    for j, clause in enumerate(clauses):
        for var in clause:
            sets[var - 1].append(j)

    return {"universe_size": num_clauses, "sets": sets}
