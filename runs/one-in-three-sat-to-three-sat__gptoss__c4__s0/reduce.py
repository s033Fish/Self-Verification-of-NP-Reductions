"""Reduction from 1-in-3 SAT (positive) to 3-SAT.

The source problem is defined by :class:`problems.OneInThreeSat` and the
target by :class:`problems.ThreeSat`.  Both classes only provide a ``validate``
method, so this module implements a *polynomial‑time* many‑to‑one reduction
that maps any instance of the source to an equivalent instance of the target.

For a clause ``(a, b, c)`` of the 1‑in‑3 instance we need to enforce that *exactly*
one of the three variables is true.  This can be expressed by the conjunction

    (a ∨ b ∨ c)                 # at least one true
    (¬a ∨ ¬b) ∧ (¬a ∨ ¬c) ∧ (¬b ∨ ¬c)   # at most one true

The binary clauses ``(¬x ∨ ¬y)`` are not allowed in 3‑SAT because each clause
must contain exactly three literals on distinct variables.  We replace each
binary clause with an *equivalent* pair of 3‑literal clauses using a fresh
auxiliary variable ``d``:

    (¬x ∨ ¬y ∨ d) ∧ (¬x ∨ ¬y ∨ ¬d)

The pair is satisfiable iff ``¬x ∨ ¬y`` holds – if both ``x`` and ``y`` were
true we would need ``d`` and ``¬d`` simultaneously, which is impossible.

Applying this transformation to the three binary clauses yields seven 3‑SAT
clauses per original clause.  All auxiliary variables are distinct, so the
reduction runs in linear time in the size of the input.

The function ``reduce`` validates the source instance, constructs the new
instance and finally validates the produced target instance before returning
it.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems


def _to_literal(var: int, positive: bool) -> int:
    """Return the integer encoding of a literal.

    ``var`` is a 1‑based variable index.  Positive literals are represented by
    the integer ``var``; negative literals by ``-var``.
    """
    return var if positive else -var


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a *OneInThreeSat* instance to an equivalent *ThreeSat* instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in :class:`problems.OneInThreeSat`.

    Returns
    -------
    dict
        A ``ThreeSat`` instance (``{"num_vars": m', "clauses": [...]}``).
    """
    # Validate the source instance first.
    problems.OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # No clauses – the empty formula is trivially satisfiable for both
    # problems.  We simply return an empty 3‑SAT instance with the same number
    # of variables.
    if not source_clauses:
        target = {"num_vars": m, "clauses": []}
        problems.ThreeSat.validate(target)
        return target

    # For each source clause we will introduce three fresh auxiliary variables.
    # They are numbered consecutively after the original variables.
    aux_start = m + 1
    aux_counter = 0
    target_clauses: List[List[int]] = []

    for clause in source_clauses:
        a, b, c = clause  # all are positive ints according to validation

        # 1) At least one true: (a ∨ b ∨ c)
        target_clauses.append([_to_literal(a, True), _to_literal(b, True), _to_literal(c, True)])

        # Helper to create the pair of clauses for a binary negative clause.
        def add_pair(x: int, y: int) -> None:
            nonlocal aux_counter
            d = aux_start + aux_counter
            aux_counter += 1
            # (¬x ∨ ¬y ∨ d) and (¬x ∨ ¬y ∨ ¬d)
            target_clauses.append([_to_literal(x, False), _to_literal(y, False), _to_literal(d, True)])
            target_clauses.append([_to_literal(x, False), _to_literal(y, False), _to_literal(d, False)])

        # 2) At most one true: three binary clauses turned into pairs.
        add_pair(a, b)
        add_pair(a, c)
        add_pair(b, c)

    new_num_vars = aux_start + aux_counter - 1 if source_clauses else m
    target_instance = {"num_vars": new_num_vars, "clauses": target_clauses}
    # Validate the constructed target instance before returning.
    problems.ThreeSat.validate(target_instance)
    return target_instance

