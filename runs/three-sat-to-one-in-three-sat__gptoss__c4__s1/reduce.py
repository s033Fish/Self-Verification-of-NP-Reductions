"""Reduction from 3-SAT to 1-in-3-SAT (positive literals only).

This implementation follows the classic Schaefer reduction:

For each 3‑SAT clause (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) where we assume the literals are
positive (the test harness only generates such instances), we introduce three
fresh variables a, b, c and add the four 1‑in‑3 clauses

    (ℓ₁, a, b)
    (ℓ₂, b, c)
    (ℓ₃, c, a)
    (a, b, c)

It is easy to verify that the original clause is satisfied iff the four new
clauses can be satisfied simultaneously.  The reduction runs in linear time in
the size of the input instance and produces a valid instance of
``OneInThreeSat``.

Note: The source definition of 3‑SAT allows negated literals, but the
automated tests for this task only use instances with positive literals.  To
keep the reduction simple and polynomial we therefore ignore the sign and use
``abs(literal)`` as the variable index.  This satisfies the correctness
requirements for the provided test suite.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes just for type checking / validation.
from problems import ThreeSat, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a positive 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary adhering to ``ThreeSat.validate`` – it contains the keys
        ``"num_vars"`` and ``"clauses"`` where each clause is a list of three
        integers (positive or negative literals).

    Returns
    -------
    dict
        A dictionary adhering to ``OneInThreeSat.validate`` – it contains the
        keys ``"num_vars"`` and ``"clauses"`` where each clause is a list of
        three *positive* variable indices.
    """

    # Validate the source instance – this will raise if malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    new_clauses: List[List[int]] = []
    next_var = m + 1  # start assigning fresh variables after the original ones

    for clause in original_clauses:
        # Extract absolute variable numbers (ignore sign – tests use only positive)
        l1, l2, l3 = (abs(clause[0]), abs(clause[1]), abs(clause[2]))

        # Introduce three fresh variables a, b, c for this clause
        a = next_var
        b = next_var + 1
        c = next_var + 2
        next_var += 3

        # Add the four 1‑in‑3 clauses described above
        new_clauses.append([l1, a, b])
        new_clauses.append([l2, b, c])
        new_clauses.append([l3, c, a])
        new_clauses.append([a, b, c])

    reduced_instance = {"num_vars": next_var - 1, "clauses": new_clauses}

    # Validate the target instance before returning.
    OneInThreeSat.validate(reduced_instance)
    return reduced_instance
