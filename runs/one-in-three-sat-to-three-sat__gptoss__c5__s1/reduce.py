"""Reduction from 1-in-3-SAT to 3-SAT.

The source problem (OneInThreeSat) expects only positive literals and asks
for an assignment where *exactly* one variable in each clause is true.

We transform each clause (a, b, c) into a set of 3‑SAT clauses that enforce
the same constraint.

For a clause (a, b, c) the exact‑one condition is equivalent to the
conjunction of:

* (a ∨ b ∨ c)                – at least one true
* (¬a ∨ ¬b) ∧ (¬a ∨ ¬c) ∧ (¬b ∨ ¬c) – at most one true

The latter three clauses have only two literals, which is not allowed in
3‑SAT.  To embed them we introduce a fresh auxiliary variable d for each
original clause and replace a 2‑literal clause (ℓ₁ ∨ ℓ₂) with the pair

    (ℓ₁ ∨ ℓ₂ ∨ d)   and   (ℓ₁ ∨ ℓ₂ ∨ ¬d)

This pair is satisfied iff (ℓ₁ ∨ ℓ₂) is satisfied, regardless of the value
chosen for d.  Adding the same auxiliary variable for all three pairwise
constraints keeps the number of new variables linear in the number of
original clauses.

The reduction runs in polynomial time: we add a constant number of clauses
per original clause and one fresh variable per original clause.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, ThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance: dict
        A dictionary adhering to the format of ``OneInThreeSat``.

    Returns
    -------
    dict
        A dictionary adhering to the format of ``ThreeSat`` such that the
        new instance is satisfiable iff the original instance is.
    """
    # Validate the source instance first – this will raise if malformed.
    OneInThreeSat.validate(instance)

    m = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses – the target can also have no clauses.
    if not source_clauses:
        target = {"num_vars": m, "clauses": []}
        ThreeSat.validate(target)
        return target

    # One fresh auxiliary variable per source clause.
    aux_start = m + 1  # first new variable index
    target_clauses: List[List[int]] = []

    for idx, clause in enumerate(source_clauses):
        a, b, c = clause  # all are positive ints per validation
        # Ensure at least one true
        target_clauses.append([a, b, c])

        # Auxiliary variable for this clause
        d = aux_start + idx

        # Helper to add padded 2‑literal clause (ℓ₁ ∨ ℓ₂)
        def add_padded(lit1: int, lit2: int) -> None:
            # (lit1 ∨ lit2 ∨ d) and (lit1 ∨ lit2 ∨ -d)
            target_clauses.append([lit1, lit2, d])
            target_clauses.append([lit1, lit2, -d])

        # At most one true – pairwise negative literals
        add_padded(-a, -b)
        add_padded(-a, -c)
        add_padded(-b, -c)

    target = {"num_vars": m + len(source_clauses), "clauses": target_clauses}
    # Validate the constructed target instance.
    ThreeSat.validate(target)
    return target

