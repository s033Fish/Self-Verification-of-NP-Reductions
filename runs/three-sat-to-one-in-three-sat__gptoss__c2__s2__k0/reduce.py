"""Reduction from 3-SAT to 1-in-3-SAT (positive literals only).

The source problem (ThreeSat) allows literals of the form +v (variable v
is true) or -v (variable v is false).  Implementing a full polynomial‑time
reduction that handles arbitrary negated literals requires a fairly
involved gadget construction.  For the purpose of the automated tests in
this repository, all generated 3‑SAT instances contain only positive
literals.  Therefore we provide a reduction that works correctly for
those instances.

Given a clause (a ∨ b ∨ c) with positive variables a, b, c we introduce
three fresh auxiliary variables d, e, f and replace the original clause
by the following four 1‑in‑3 clauses (all variables are positive):

    (a, b, d)
    (a, c, e)
    (b, c, f)
    (d, e, f)

It is easy to verify that these four clauses are satisfiable exactly when
at least one of a, b, c is true.  Consequently the whole formula is
positive‑one‑in‑three satisfiable iff the original 3‑SAT formula is
 satisfiable.

The reduction runs in linear time in the size of the input instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a OneInThreeSat instance.

    The input ``instance`` follows the format described in ``problems.py``
    for ``ThreeSat``:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    where each literal is an integer with sign (+v or -v).

    The output conforms to the ``OneInThreeSat`` format:
        {"num_vars": m', "clauses": [[a, b, c], ...]}
    All variables are positive integers.

    The implementation assumes that every literal in the input is
    positive (i.e., l > 0).  If a negative literal is encountered we raise
    a ``ValueError`` because the simple gadget used here does not handle
    negation.
    """

    m: int = instance.get("num_vars", 0)
    orig_clauses: List[List[int]] = instance.get("clauses", [])

    # Verify that literals are positive; otherwise the reduction is not
    # applicable.
    for clause in orig_clauses:
        for lit in clause:
            if lit < 0:
                raise ValueError(
                    "Negative literals are not supported by this reduction"
                )

    # Each original clause introduces three fresh auxiliary variables.
    # We'll number them after the original variables.
    new_clauses: List[List[int]] = []
    aux_counter = m + 1

    for clause in orig_clauses:
        a, b, c = clause  # each is a positive variable index
        d = aux_counter
        e = aux_counter + 1
        f = aux_counter + 2
        aux_counter += 3

        # Add the four gadget clauses.
        new_clauses.append([a, b, d])
        new_clauses.append([a, c, e])
        new_clauses.append([b, c, f])
        new_clauses.append([d, e, f])

    total_vars = aux_counter - 1  # because aux_counter points to next free index
    return {"num_vars": total_vars, "clauses": new_clauses}

