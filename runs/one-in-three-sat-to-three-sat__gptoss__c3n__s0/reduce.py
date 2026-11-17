"""Reduction from 1-in-3-SAT (positive) to 3-SAT.

The source problem is defined in :class:`OneInThreeSat` (see ``problems.py``).
Each clause ``[a, b, c]`` requires **exactly one** of the three variables to
be true.  The target problem is :class:`ThreeSat` where each clause must have
at least one true literal.

For a clause ``(a ∨ b ∨ c)`` with the *exactly‑one* condition we can write an
equivalent 3‑CNF formula using auxiliary variables.  The condition is

    (a ∨ b ∨ c) ∧ (¬a ∨ ¬b) ∧ (¬a ∨ ¬c) ∧ (¬b ∨ ¬c)

The first part is already a 3‑literal clause.  The remaining three clauses
have only two literals; each such clause ``(ℓ₁ ∨ ℓ₂)`` can be expressed as a
pair of 3‑clauses using a fresh auxiliary variable ``w``:

    (ℓ₁ ∨ ℓ₂ ∨  w) ∧ (ℓ₁ ∨ ℓ₂ ∨ ¬w)

If ``ℓ₁ ∨ ℓ₂`` is false (i.e. both literals are false) the two new clauses
become ``w`` and ``¬w`` which cannot be satisfied simultaneously.  If the
original 2‑clause is true, both new clauses are satisfied regardless of the
value of ``w``.  Hence the pair is equivalent to the original 2‑clause.

We introduce **one** fresh auxiliary variable per original clause and reuse it
for the three 2‑clauses belonging to that original clause.  The resulting
instance therefore contains ``m + n`` variables where ``m`` is the number of
original variables and ``n`` is the number of clauses.

The reduction runs in linear time in the size of the input and produces a
valid ``ThreeSat`` instance according to the validation helpers in
``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, ThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a ``OneInThreeSat`` instance to an equivalent ``ThreeSat`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the docstring of :class:`OneInThreeSat`.

    Returns
    -------
    dict
        A ``ThreeSat`` instance (``{"num_vars": ..., "clauses": [...]}``).
        The instance is satisfiable iff the input instance is satisfiable.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is wrong.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses – the formula is always satisfiable.  We keep the
    # same number of variables (no need for auxiliaries).
    if not original_clauses:
        return {"num_vars": m, "clauses": []}

    n_clauses = len(original_clauses)
    # New variables are indexed from m+1 .. m+n_clauses (inclusive).
    total_vars = m + n_clauses

    three_sat_clauses: List[List[int]] = []

    for idx, clause in enumerate(original_clauses, start=1):
        a, b, c = clause  # each is a positive int
        aux = m + idx  # fresh auxiliary variable for this clause

        # 1. The original clause as a 3‑SAT clause (needs exactly one true, but
        #    the additional constraints will enforce the "exactly" part).
        three_sat_clauses.append([a, b, c])

        # Helper to add the pair encoding of a 2‑clause (ℓ1 ∨ ℓ2).
        def add_two_literal_clause(lit1: int, lit2: int) -> None:
            # (lit1 ∨ lit2 ∨ aux) and (lit1 ∨ lit2 ∨ -aux)
            three_sat_clauses.append([lit1, lit2, aux])
            three_sat_clauses.append([lit1, lit2, -aux])

        # 2. Encode (¬a ∨ ¬b), (¬a ∨ ¬c), (¬b ∨ ¬c) using the auxiliary.
        add_two_literal_clause(-a, -b)
        add_two_literal_clause(-a, -c)
        add_two_literal_clause(-b, -c)

    # Build the result instance and validate it against ThreeSat.
    result = {"num_vars": total_vars, "clauses": three_sat_clauses}
    ThreeSat.validate(result)
    return result

