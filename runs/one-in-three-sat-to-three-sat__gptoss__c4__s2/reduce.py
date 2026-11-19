"""Reduction from 1-in-3 SAT (positive) to 3-SAT.

The source problem ``OneInThreeSat`` expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where ``a, b, c`` are distinct positive integers (variables) and a clause is
satisfied iff **exactly one** of the three variables is assigned ``True``.

The target problem ``ThreeSat`` expects instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``v`` (positive for ``v`` is True) or
``-v`` (negative for ``v`` is False).  A clause is satisfied iff at least one
literal is true.

For each source clause ``(x ∨ y ∨ z)`` we produce the following five 3‑SAT
clauses, a classic gadget that is equivalent to the *exactly‑one* constraint:

    1.  ( x  ∨  y  ∨  z )
    2.  (¬x ∨ ¬y ∨ ¬z)
    3.  ( x  ∨ ¬y ∨ ¬z)
    4.  (¬x ∨  y  ∨ ¬z)
    5.  (¬x ∨ ¬y ∨  z )

All literals refer only to the original variables, so no auxiliary variables
are introduced.  The gadget is easy to verify: it is satisfied exactly when
one of ``x, y, z`` is true.

The reduction runs in linear time in the size of the input (three new clauses
per source clause), which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict

from problems import OneInThreeSat, ThreeSat


def _gadget(clause: List[int]) -> List[List[int]]:
    """Return the 5‑clause 3‑SAT gadget for a source clause.

    ``clause`` is a list ``[a, b, c]`` of three **positive** variable indices.
    The returned list contains five clauses, each a list of three literals.
    """
    a, b, c = clause
    # Positive literals are just the variable number, negative literals are
    # the negated integer.
    return [
        [a, b, c],           # at least one true
        [-a, -b, -c],        # not all true
        [a, -b, -c],         # not both b and c true
        [-a, b, -c],         # not both a and c true
        [-a, -b, c],         # not both a and b true
    ]


def reduce(instance: Dict) -> Dict:
    """Reduce a ``OneInThreeSat`` instance to an equivalent ``ThreeSat``.

    The function validates the input using ``OneInThreeSat.validate`` and
    returns a new dictionary suitable for ``ThreeSat.validate``.  The number
    of variables stays the same; each source clause is replaced by the five
    clauses from :func:`_gadget`.
    """
    # Validate source instance (may raise InvalidInstance)
    OneInThreeSat.validate(instance)

    m = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    target_clauses: List[List[int]] = []
    for cl in source_clauses:
        target_clauses.extend(_gadget(cl))

    target_instance = {"num_vars": m, "clauses": target_clauses}
    # Validate the produced target instance to catch programming errors.
    ThreeSat.validate(target_instance)
    return target_instance

