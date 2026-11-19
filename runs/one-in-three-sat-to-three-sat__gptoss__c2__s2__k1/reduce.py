"""Reduction from 1-in-3-SAT (positive) to 3-SAT.

The source problem (``OneInThreeSat``) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where ``a, b, c`` are distinct positive integers in ``1..m`` and a clause is
satisfied iff **exactly one** of its three variables is assigned ``True``.

The target problem (``ThreeSat``) expects instances of the form::

    {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

where each ``li`` is a signed integer.  ``+v`` (or simply ``v``) denotes the
positive literal *v* and ``-v`` denotes the negated literal.  A clause is
 satisfied iff at least one of its three literals is ``True``.

We provide a polynomial‑time many‑one reduction.  For each source clause
``(x ∨ y ∨ z)`` we need to enforce two conditions on the target formula:

1. **At least one** of the three variables is true – this is directly the
   3‑SAT clause ``[x, y, z]``.
2. **At most one** of the three variables is true – for each pair we add a
   clause ``(¬x ∨ ¬y)`` etc.  Because the target format requires exactly three
   literals on distinct variables we pad these 2‑CNF clauses with a variable
   that is forced to be *false*.

Forcing a variable ``f`` to be false can be done with four 3‑SAT clauses that
use two fresh auxiliary variables ``a`` and ``b`` (see e.g. Schaefer's trick)::

    (¬f ∨  a ∨  b)
    (¬f ∨ ¬a ∨  b)
    (¬f ∨  a ∨ ¬b)
    (¬f ∨ ¬a ∨ ¬b)

If ``f`` were true, the four clauses would require ``a`` to be simultaneously
true and false, which is impossible.  Hence any satisfying assignment must set
``f = False``.  When ``f`` is false the clauses are trivially satisfied, so ``f``
behaves exactly like the constant ``False``.

Using this constant we can encode the pairwise at‑most‑one constraints as::

    (¬x ∨ ¬y ∨ f)   # equivalent to (¬x ∨ ¬y) because f = False
    (¬x ∨ ¬z ∨ f)
    (¬y ∨ ¬z ∨ f)

The reduction therefore proceeds as follows:

* If the source instance has no clauses we return an empty 3‑SAT instance –
  both are trivially satisfiable.
* Otherwise we introduce three new variables: ``f`` (the forced‑false
  constant) and auxiliaries ``a`` and ``b``.  We add the four gadget clauses
  that force ``f`` to be false.
* For each source clause ``[x, y, z]`` we add the four target clauses described
  above.

The construction uses a linear number of new clauses and a constant number of
new variables, so it runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``OneInThreeSat`` instance to a ``ThreeSat`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of positive ints).

    Returns
    -------
    dict
        A ``ThreeSat`` instance satisfying the specification described in the
        module docstring.
    """

    m: int = instance.get("num_vars", 0)
    source_clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: empty formula – both source and target are trivially YES.
    if not source_clauses:
        return {"num_vars": m, "clauses": []}

    # Introduce three fresh variables: f (forced false), a, b.
    f = m + 1
    a = m + 2
    b = m + 3
    total_vars = b

    target_clauses: List[List[int]] = []

    # Gadget that forces f = False.
    # (¬f ∨  a ∨  b)
    target_clauses.append([-f, a, b])
    # (¬f ∨ ¬a ∨  b)
    target_clauses.append([-f, -a, b])
    # (¬f ∨  a ∨ ¬b)
    target_clauses.append([-f, a, -b])
    # (¬f ∨ ¬a ∨ ¬b)
    target_clauses.append([-f, -a, -b])

    # Encode each 1‑in‑3 clause.
    for clause in source_clauses:
        if len(clause) != 3:
            # Defensive: the source validator guarantees length 3, but we keep
            # the code robust.
            raise ValueError("Each clause must contain exactly three variables")
        x, y, z = clause
        # At least one true.
        target_clauses.append([x, y, z])
        # At most one true – padded with the forced‑false constant f.
        target_clauses.append([-x, -y, f])
        target_clauses.append([-x, -z, f])
        target_clauses.append([-y, -z, f])

    return {"num_vars": total_vars, "clauses": target_clauses}

