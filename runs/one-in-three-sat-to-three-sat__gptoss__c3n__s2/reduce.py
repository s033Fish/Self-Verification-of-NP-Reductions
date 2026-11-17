"""Reduction from 1-in-3-SAT (positive literals) to 3-SAT.

The source problem is :class:`OneInThreeSat` defined in ``problems.py``.
Each clause contains three *positive* variables and the formula is satisfied
iff exactly one of the three variables is true in every clause.

The target problem is :class:`ThreeSat`.  A clause must contain three literals
on three distinct variables and is satisfied iff at least one literal is
true.

For a source clause ``(a, b, c)`` we enforce the following constraints using
3‑SAT clauses:

* **At least one true** – the clause ``(a ∨ b ∨ c)``.
* **At most one true** – for each pair ``(x, y)`` among ``{a, b, c}`` we need
  ``¬x ∨ ¬y``.  Since 3‑SAT clauses must have exactly three literals, we replace
  a 2‑literal clause ``(ℓ₁ ∨ ℓ₂)`` with two 3‑literal clauses introducing a fresh
  auxiliary variable ``t``:

  ``(ℓ₁ ∨ ℓ₂ ∨ t) ∧ (ℓ₁ ∨ ℓ₂ ∨ ¬t)``

  This construction is equivalent to the original 2‑literal clause because the
  two new clauses are simultaneously satisfied iff ``ℓ₁ ∨ ℓ₂`` is true.

The reduction runs in polynomial time: for each source clause we add one
3‑literal clause and three pairs each generate two new clauses, i.e. seven
clauses total.  The number of variables grows by three fresh auxiliaries per
source clause, which is also polynomial.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3‑SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described in
        :class:`OneInThreeSat`.

    Returns
    -------
    dict
        A 3‑SAT instance (dictionary with ``"num_vars"`` and ``"clauses"``) that
        is satisfiable exactly when the input instance is.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    new_clauses: List[List[int]] = []
    next_var = m + 1  # first auxiliary variable index

    for clause in source_clauses:
        a, b, c = clause  # variables are guaranteed distinct and positive
        # 1. At least one of a,b,c is true
        new_clauses.append([a, b, c])

        # 2. At most one true – encode pairwise ¬x ∨ ¬y using auxiliaries
        pairs = [(a, b), (a, c), (b, c)]
        for x, y in pairs:
            t = next_var
            next_var += 1
            # (¬x ∨ ¬y ∨ t) ∧ (¬x ∨ ¬y ∨ ¬t)
            new_clauses.append([-x, -y, t])
            new_clauses.append([-x, -y, -t])

    # The total number of variables after adding auxiliaries
    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": new_clauses}

