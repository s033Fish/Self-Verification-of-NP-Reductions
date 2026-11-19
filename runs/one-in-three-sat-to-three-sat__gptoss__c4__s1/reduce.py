"""Reduction from 1-in-3 SAT (positive) to 3-SAT.

The source problem is defined in :class:`OneInThreeSat` and expects instances
{"num_vars": m, "clauses": [[a, b, c], ...]} where each clause contains
three *positive* literals.  The target problem is :class:`ThreeSat` whose
instances have the same shape but literals may be positive or negative.

For a clause (a, b, c) we need to enforce that **exactly one** of the three
variables is true.  This can be expressed as the conjunction of:

* At least one true: ``(a ∨ b ∨ c)``.
* At most one true: for each pair we need ``(¬a ∨ ¬b)``.

The pairwise constraints are 2‑CNF clauses.  To embed them into a 3‑CNF we use a
standard Tseitin‑style trick: for a 2‑literal clause ``(ℓ₁ ∨ ℓ₂)`` introduce a
fresh auxiliary variable ``p`` and replace it by the pair of 3‑clauses

``(ℓ₁ ∨ ℓ₂ ∨  p)`` and ``(ℓ₁ ∨ ℓ₂ ∨ ¬p)``.

These two clauses are equivalent to the original 2‑CNF clause because they are
simultaneously satisfiable iff at least one of ``ℓ₁, ℓ₂`` is true.  If both are
false they force ``p`` to be both true and false, which is impossible.

Applying this transformation to each of the three pairwise constraints yields
seven 3‑clauses per original clause.  All auxiliary variables are distinct and
greater than the original ``num_vars``.

The reduction runs in polynomial time and preserves satisfiability: a
assignment satisfying the original 1‑in‑3‑SAT instance can be extended arbitrarily
to the auxiliary variables to satisfy the produced 3‑SAT instance, and any
model of the 3‑SAT instance must satisfy the original exact‑one condition.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import OneInThreeSat, ThreeSat


def _pairwise_constraints(a: int, b: int, aux: int) -> List[List[int]]:
    """Return the two 3‑clauses encoding the 2‑CNF clause (¬a ∨ ¬b).

    ``aux`` is a fresh variable index.  The returned clauses are:
    ``[-a, -b,  aux]`` and ``[-a, -b, -aux]``.
    """
    return [[-a, -b, aux], [-a, -b, -aux]]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a *positive* 1‑in‑3‑SAT instance to an equivalent 3‑SAT instance.

    The function validates the input using :class:`OneInThreeSat.validate` and
    validates the output with :class:`ThreeSat.validate` before returning.
    """
    # Validate source instance.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # If there are no clauses, the formula is trivially satisfiable; we can
    # return an empty 3‑SAT instance with the same number of variables.
    if not source_clauses:
        result = {"num_vars": m, "clauses": []}
        ThreeSat.validate(result)
        return result

    new_clauses: List[List[int]] = []
    next_aux = m + 1  # first auxiliary variable index

    for clause in source_clauses:
        a, b, c = clause  # each clause already has exactly three distinct vars
        # At least one true.
        new_clauses.append([a, b, c])
        # At most one true – encode each pairwise (¬x ∨ ¬y) using two 3‑clauses.
        for x, y in ((a, b), (a, c), (b, c)):
            aux = next_aux
            next_aux += 1
            new_clauses.extend(_pairwise_constraints(x, y, aux))

    result = {"num_vars": next_aux - 1, "clauses": new_clauses}
    # Validate the produced 3‑SAT instance.
    ThreeSat.validate(result)
    return result
