"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Idea
----
Represent the clause structure in a positional (base-B) number system with one
digit position per clause.  Choose B = 4; every clause contains exactly 3
distinct variables, so at most 3 chosen numbers can contribute a 1 to any
single clause position, hence no carries ever occur (max digit is 3 < B).

For each variable v (1..m) build one number whose digit in clause-position j
is 1 if v occurs in clause j, else 0.  The target has digit 1 in every clause
position.

A sub-list of the numbers sums to the target iff for every clause position the
chosen numbers contribute exactly one 1, i.e. exactly one of the clause's three
variables is chosen.  Interpreting "chosen" as "true" (and unchosen as false)
this is precisely an assignment making exactly one variable true per clause.

Variables that occur in no clause get the number 0 and never matter.
A formula with no clauses gives numbers = [] and target = 0 (yes).
"""

from __future__ import annotations

from typing import Any

BASE = 4  # > 3 = maximum number of chosen variables inside one clause


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    powers = [BASE ** j for j in range(len(clauses))]
    target = sum(powers)

    numbers = []
    for var in range(1, num_vars + 1):
        value = 0
        for j, clause in enumerate(clauses):
            if var in clause:
                value += powers[j]
        numbers.append(value)

    return {"numbers": numbers, "target": target}
