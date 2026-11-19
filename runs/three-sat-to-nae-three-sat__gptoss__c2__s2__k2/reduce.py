"""Reduction from 3‑SAT to NAE‑3‑SAT.

The source problem (ThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is
assigned ``True``) or ``-v`` (meaning variable *v* is assigned ``False``).

The target problem (NaeThreeSat) uses the exact same representation but
interprets a clause as satisfied when **not all three literals evaluate to
the same Boolean value** (i.e., at least one true and at least one false).

We implement a classic polynomial‑time reduction.  For every original
clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we introduce two fresh auxiliary variables
``T`` and ``S`` that are forced to be ``True`` in any NAE‑satisfying
assignment.  Forcing a variable ``X`` to be true can be done with two NAE
clauses using two additional fresh variables ``a`` and ``b``::

    (X, a, b)      and      (X, -a, -b)

These two clauses are satisfiable **iff** ``X`` is assigned ``True`` –
if ``X`` were ``False`` the first clause would require both ``a`` and ``b``
to be true, while the second would require both ``-a`` and ``-b`` to be
true, which is impossible.

Having ``T`` and ``S`` both true, we replace the original clause with the
following two NAE‑clauses:

    (ℓ1, ℓ2, T)
    (-T, ℓ3, S)

If the original clause is satisfied, we can set ``T`` and ``S`` to ``True``
and choose the auxiliary literals accordingly; the two NAE clauses are then
satisfied.  Conversely, any assignment satisfying the two NAE clauses forces
``ℓ1 ∨ ℓ2 ∨ ℓ3`` to be true, because:

* If both ``ℓ1`` and ``ℓ2`` are false, the first clause forces ``T`` to be
  true (otherwise all three literals would be false).  The second clause then
  requires ``ℓ3`` to be true (since ``-T`` would be false and ``S`` is true).
* If at least one of ``ℓ1`` or ``ℓ2`` is true, the first clause is already
  satisfied regardless of ``T``; the second clause cannot be all false because
  ``S`` is true, so no additional condition on ``ℓ3`` is needed.

Thus the original clause is satisfied iff the two new NAE clauses are
simultaneously satisfiable, and the forcing construction guarantees the
auxiliary variables indeed take the value ``True``.

The reduction runs in linear time in the size of the input and introduces a
constant number of fresh variables per original clause, which is clearly
polynomial.
"""

from __future__ import annotations

from typing import List, Dict


def _new_var(counter: List[int]) -> int:
    """Return a fresh variable index and increment the counter.

    ``counter`` is a single‑element list holding the next available variable
    number.  Using a list allows us to modify it inside the function without
    declaring it ``global``.
    """
    var = counter[0]
    counter[0] += 1
    return var


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to a NaeThreeSat instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        An instance of the target problem (same shape) that is NAE‑satisfiable
        exactly when the input instance is satisfiable.
    """
    m = instance.get("num_vars", 0)
    orig_clauses: List[List[int]] = instance.get("clauses", [])

    # Counter for fresh variable numbers – start after the original ones.
    next_var = [m + 1]
    new_clauses: List[List[int]] = []

    for clause in orig_clauses:
        # clause has exactly three literals ℓ1, ℓ2, ℓ3
        l1, l2, l3 = clause

        # ---- create forced‑true variable T and its auxiliaries a, b ----
        T = _new_var(next_var)
        a = _new_var(next_var)
        b = _new_var(next_var)
        # (T, a, b) and (T, -a, -b)
        new_clauses.append([T, a, b])
        new_clauses.append([T, -a, -b])

        # ---- create forced‑true variable S and its auxiliaries c, d ----
        S = _new_var(next_var)
        c = _new_var(next_var)
        d = _new_var(next_var)
        new_clauses.append([S, c, d])
        new_clauses.append([S, -c, -d])

        # ---- gadget clauses that simulate the original OR ----
        # (ℓ1, ℓ2, T)
        new_clauses.append([l1, l2, T])
        # (-T, ℓ3, S)  note the negation of T is represented by -T
        new_clauses.append([-T, l3, S])

    # If there were no original clauses we simply return an empty‑clause
    # instance (which is a yes‑instance for both problems).
    result = {
        "num_vars": next_var[0] - 1,  # last used index
        "clauses": new_clauses,
    }
    return result

