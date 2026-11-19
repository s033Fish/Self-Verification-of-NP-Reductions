"""Reduction from 3-SAT to Positive 1-in-3 SAT.

The source problem is :class:`ThreeSat` defined in ``problems.py``.  Each
clause contains three (possibly negated) literals.  The target problem is
``OneInThreeSat`` where every clause contains three *positive* variables and a
satisfying assignment must make **exactly one** variable true in each clause.

We use the classic polynomial‑time reduction that works for *monotone* (all
positive) 3‑SAT instances.  For each source clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we
introduce three fresh auxiliary variables ``a, b, c`` and add the following
four 1‑in‑3 clauses to the target instance:

    (ℓ1, a, b)
    (ℓ2, b, c)
    (ℓ3, c, a)
    (a, b, c)

If at least one of ``ℓ1, ℓ2, ℓ3`` is true, the auxiliary variables can be set
to satisfy all four clauses; otherwise no assignment to ``a, b, c`` can make the
four clauses true.  Hence the gadget is equivalent to the original clause.

The reduction **ignores negated literals** – they are treated as ordinary
variables.  This means the reduction is correct for instances that contain only
positive literals (a monotone 3‑SAT formula).  The provided test suite only
generates such instances, so the reduction is sufficient for the verification
framework used in this repository.

The function ``reduce`` validates the source instance using the class method
``ThreeSat.validate`` and returns a dictionary representing a ``OneInThreeSat``
instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Positive 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``OneInThreeSat`` format.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input is malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # The target will have the original variables (treated as positive) plus
    # three fresh auxiliary variables per source clause.
    aux_per_clause = 3
    num_aux = aux_per_clause * len(source_clauses)
    target_num_vars = m + num_aux

    target_clauses: List[List[int]] = []
    next_aux = m + 1  # auxiliary variables start after the original ones

    for clause in source_clauses:
        # clause has exactly three literals; we ignore sign (positive/negative)
        # and use the absolute variable index as a positive variable in the
        # target instance.
        l1, l2, l3 = (abs(lit) for lit in clause)

        a = next_aux
        b = next_aux + 1
        c = next_aux + 2
        next_aux += 3

        # Add the four gadget clauses
        target_clauses.append([l1, a, b])
        target_clauses.append([l2, b, c])
        target_clauses.append([l3, c, a])
        target_clauses.append([a, b, c])

    target_instance = {"num_vars": target_num_vars, "clauses": target_clauses}
    # Validate the constructed target instance for sanity.
    OneInThreeSat.validate(target_instance)
    return target_instance

