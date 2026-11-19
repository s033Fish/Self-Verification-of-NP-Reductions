"""Reduction from 3-SAT (SOURCE) to NAE-3-SAT (TARGET).

The reduction follows a classic polynomial‑time many‑one transformation.
For each 3‑SAT clause (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) we introduce a fresh auxiliary variable
``z_i`` and replace the clause by the two NAE‑3‑SAT clauses

    (ℓ₁, ℓ₂,  z_i)
    (¬z_i, ℓ₃,  t)

where ``t`` is a single global auxiliary variable that appears in every
second clause.  The variable ``t`` is forced to be **True** by adding the
single NAE clause ``(t, t, f)`` together with a second clause ``(f, f, f)``
that forces ``f`` to be **False**.  (In NAE‑3‑SAT a clause is unsatisfied
iff all three literals have the same truth value, so ``(f,f,f)`` can never be
satisfied – the only way for the whole formula to be satisfiable is for ``f``
to be assigned ``False`` and consequently ``t`` must be ``True``.)

Intuitively, the first clause forces at least one of ``ℓ₁`` or ``ℓ₂`` to differ
from ``z_i``; the second clause forces at least one of ``ℓ₃`` or ``¬z_i`` to
differ from ``t``.  Because ``t`` is true, the second clause is satisfied iff
``¬z_i`` is false **or** ``ℓ₃`` is true, i.e. iff ``z_i`` is true **or** ``ℓ₃``
is true.  Combining the two clauses yields exactly the condition
``ℓ₁ ∨ ℓ₂ ∨ ℓ₃``.

The construction uses a linear number of new variables and clauses, so it
runs in polynomial time.

The implementation below follows the specification of ``SOURCE`` and
``TARGET`` as described in ``problems.py``.  It validates the input using the
``ThreeSat.validate`` method and returns a dictionary suitable for the
``NaeThreeSat`` class.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, NaeThreeSat


def _literal_to_int(literal: int) -> int:
    if not isinstance(literal, int):  # pragma: no cover – defensive
        raise ValueError("literal must be an int")
    return literal


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    ThreeSat.validate(instance)

    m = instance["num_vars"]
    orig_clauses: List[List[int]] = instance["clauses"]

    # Auxiliary variables: global t (True) and f (False), plus one z_i per clause.
    aux_start = m + 1
    t_var = aux_start       # will be forced true
    f_var = aux_start + 1   # will be forced false
    z_start = aux_start + 2

    new_clauses: List[List[int]] = []

    # Force t = True and f = False using two NAE clauses.
    # Clause (t, t, f) forces t != f, clause (f, f, t) forces f != t.
    new_clauses.append([ t_var, t_var, f_var ])
    new_clauses.append([ f_var, f_var, t_var ])

    for i, clause in enumerate(orig_clauses):
        l1, l2, l3 = map(_literal_to_int, clause)
        zi = z_start + i
        new_clauses.append([ l1, l2, zi ])
        new_clauses.append([ -zi, l3, t_var ])

    total_vars = m + 2 + len(orig_clauses)  # t, f, and one zi per original clause

    reduced_instance = {
        "num_vars": total_vars,
        "clauses": new_clauses,
    }

    NaeThreeSat.validate(reduced_instance)
    return reduced_instance

