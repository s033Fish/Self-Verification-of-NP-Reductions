"""Reduction from 1-in-3 SAT (positive literals only) to 3‑SAT.

The source problem (``OneInThreeSat``) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where ``a, b, c`` are distinct variable indices (positive integers) and a
solution must assign **exactly one** true variable in each clause.

The target problem (``ThreeSat``) expects instances where every clause has
exactly three literals (positive or negative) on three distinct variables.
A formula is satisfiable iff each clause contains at least one true literal.

For each source clause ``(x ∨ y ∨ z)`` we use the classic polynomial‑time
gadget that enforces *exactly one* of ``x, y, z`` to be true using only
3‑SAT clauses.  Introduce three fresh auxiliary variables ``a, b, c`` and add
the following four clauses (all of length three and on distinct variables)::

    ( x ∨ y ∨  a )
    ( x ∨ z ∨  b )
    ( y ∨ z ∨  c )
    ( ¬a ∨ ¬b ∨ ¬c )

It is easy to verify that these four clauses are simultaneously satisfiable
iff exactly one of ``x, y, z`` is true.  The reduction therefore replaces each
1‑in‑3 clause with the four 3‑SAT clauses above, using disjoint auxiliary
variables for each original clause.  The construction runs in time linear in
the size of the input formula and produces a valid ``ThreeSat`` instance.

The function ``reduce`` implements this transformation.  It returns a new
dictionary compatible with the ``ThreeSat`` format defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Convert a 1‑in‑3‑SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of positive integers).  The instance conforms to
        the ``OneInThreeSat`` specification.

    Returns
    -------
    dict
        A dictionary representing a ``ThreeSat`` instance.  The number of
        variables is increased by three fresh variables per original clause,
        and the clause list contains the four 3‑SAT clauses described in the
        module docstring.
    """

    # Original number of variables and the list of 1‑in‑3 clauses.
    m: int = instance.get("num_vars", 0)
    src_clauses: List[List[int]] = instance.get("clauses", [])

    # The resulting list of 3‑SAT clauses.
    target_clauses: List[List[int]] = []

    # Fresh variable counter – start after the existing variables.
    next_var: int = m + 1

    for clause in src_clauses:
        # Each clause is guaranteed to contain exactly three distinct
        # positive integers according to the source specification.
        if len(clause) != 3:
            # Defensive programming – if the input is malformed we simply
            # skip the clause.  Validation is performed elsewhere in the
            # framework; this guard prevents a crash during reduction.
            continue
        x, y, z = clause

        # Allocate three fresh auxiliary variables for this clause.
        a = next_var
        b = next_var + 1
        c = next_var + 2
        next_var += 3

        # Add the four clauses of the gadget.
        target_clauses.append([x, y, a])   # (x ∨ y ∨ a)
        target_clauses.append([x, z, b])   # (x ∨ z ∨ b)
        target_clauses.append([y, z, c])   # (y ∨ z ∨ c)
        target_clauses.append([-a, -b, -c])  # (¬a ∨ ¬b ∨ ¬c)

    # The total number of variables includes the original ones plus all
    # auxiliaries introduced.
    total_vars = next_var - 1

    return {"num_vars": total_vars, "clauses": target_clauses}

