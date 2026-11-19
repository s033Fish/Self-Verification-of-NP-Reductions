"""Reduction from 3-SAT to NAE-3-SAT.

We use a standard polynomial‑time reduction.
We introduce a fresh variable f that is forced to be False by the two
NAE‑3‑SAT clauses (f, a, b) and (f, -a, -b) where a and b are fresh
auxiliary variables. These clauses cannot be satisfied simultaneously when
f = True, so any satisfying assignment must set f = False.

With f = False, a clause NAE(x, y, f) is equivalent to the binary OR
(x ∨ y): the clause is unsatisfied only when x = y = False.

For each original 3‑SAT clause (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) we introduce a fresh variable y
and add the two NAE clauses
    (ℓ₁, ℓ₂, y)
    (¬y, ℓ₃, f)
These two clauses together are satisfiable iff (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) holds.
All clauses have three distinct variables, satisfying the problem
requirements.
"""

from __future__ import annotations

from typing import List, Dict


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to an equivalent NaeThreeSat instance.

    Parameters
    ----------
    instance: dict with keys "num_vars" and "clauses" as defined for ThreeSat.

    Returns
    -------
    dict representing a NaeThreeSat instance that is satisfiable iff the
    original instance is satisfiable.
    """
    m = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # Fresh variables:
    # f : variable that will be forced to False.
    # a, b : auxiliary variables used in two helper clauses that together
    #         enforce f = False without repeating a variable inside a clause.
    f = m + 1
    a = m + 2
    b = m + 3
    next_var = m + 4  # first y variable index (one per original clause)

    new_clauses: List[List[int]] = []
    # Helper clauses to force f = False. Both clauses contain three distinct
    # variables, satisfying the problem constraints.
    new_clauses.append([f, a, b])
    new_clauses.append([f, -a, -b])

    # For each original clause, add the gadget using a fresh y variable.
    for clause in original_clauses:
        if len(clause) != 3:
            raise ValueError("All source clauses must have exactly three literals")
        l1, l2, l3 = clause
        y = next_var
        next_var += 1
        # (l1, l2, y)
        new_clauses.append([l1, l2, y])
        # (¬y, l3, f)
        new_clauses.append([-y, l3, f])

    return {"num_vars": next_var - 1, "clauses": new_clauses}

