"""Reduction from 1-in-3-SAT (positive literals) to 3-SAT.

The source problem is ``OneInThreeSat`` whose instances are of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *positive* variables and the formula is
satisfiable iff exactly one variable in each clause can be set to ``True``.

The target problem is ``ThreeSat`` whose instances are of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``v`` (positive for the variable
``v``) or ``-v`` (negated).  Every clause must contain three *different*
variables and at least one literal must be true.

The reduction is classic: for each original clause ``(x, y, z)`` we enforce
``(x ∨ y ∨ z)`` (at least one true) and the three pairwise constraints
``¬x ∨ ¬y``, ``¬x ∨ ¬z`` and ``¬y ∨ ¬z`` (at most one true).  The pairwise
constraints are binary clauses, but ``ThreeSat`` only allows clauses of
size three.  We transform a binary clause ``(¬a ∨ ¬b)`` into two 3‑clauses
using a fresh auxiliary variable ``w``:

    (¬a ∨ ¬b ∨  w)
    (¬a ∨ ¬b ∨ -w)

Both clauses must be satisfied; if ``a`` and ``b`` were true, the first
clause would require ``w`` to be true while the second would require ``w``
to be false – impossible.  Hence the pairwise constraint is correctly
encoded.

The construction is polynomial: for each source clause we add one original
3‑clause and six auxiliary 3‑clauses, introducing six fresh variables.  The
total number of variables grows linearly with the size of the input.

The ``reduce`` function implements this transformation and returns a valid
``ThreeSat`` instance.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Transform a ``OneInThreeSat`` instance into a ``ThreeSat`` instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
        where ``a, b, c`` are positive integers (1‑based variable indices).

    Returns
    -------
    dict
        ``{"num_vars": m', "clauses": [[l1, l2, l3], ...]}`` suitable for the
        ``ThreeSat`` problem.
    """

    m: int = instance.get("num_vars", 0)
    source_clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: no clauses – the formula is trivially satisfiable.
    if not source_clauses:
        return {"num_vars": m, "clauses": []}

    # We'll collect clauses for the target instance.
    target_clauses: List[List[int]] = []

    # The next fresh variable index.
    next_var: int = m + 1

    for clause in source_clauses:
        # Each clause is guaranteed to have exactly three distinct positive vars.
        a, b, c = clause

        # 1. At least one true: (a ∨ b ∨ c)
        target_clauses.append([a, b, c])

        # 2. Pairwise at‑most‑one constraints.
        pairs = [(a, b), (a, c), (b, c)]
        for (x, y) in pairs:
            # Introduce a fresh auxiliary variable w.
            w = next_var
            next_var += 1
            # Encode (¬x ∨ ¬y) as two 3‑clauses:
            #   (¬x ∨ ¬y ∨  w) and (¬x ∨ ¬y ∨ -w)
            target_clauses.append([-x, -y,  w])
            target_clauses.append([-x, -y, -w])

    # Total number of variables after adding auxiliaries.
    total_vars = next_var - 1

    return {"num_vars": total_vars, "clauses": target_clauses}

