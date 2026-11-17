"""Reduction from 1-in-3-SAT (positive literals only) to 3-SAT.

The source problem (``OneInThreeSat``) asks for an assignment where **exactly
one** variable in each clause of three *positive* variables is true.  A classic
CNF encoding of the ``exactly‑one`` constraint for variables ``a, b, c`` is:

    (a ∨ b ∨ c)               # at least one true
    (¬a ∨ ¬b) ∧ (¬a ∨ ¬c) ∧ (¬b ∨ ¬c)   # no two true simultaneously

The source problem already uses this encoding internally (see
``OneInThreeSat.is_yes``).  However, the 3‑SAT target (``ThreeSat``) requires **
+every clause to contain exactly three literals on three distinct variables** –
+2‑literal clauses are not permitted.

To transform a 2‑literal clause ``(¬x ∨ ¬y)`` into an equivalent set of 3‑literal
clauses we introduce a fresh dummy variable ``d`` and add the pair:

    (¬x ∨ ¬y ∨ d) ∧ (¬x ∨ ¬y ∨ ¬d)

Both clauses together are logically equivalent to ``(¬x ∨ ¬y)`` because the
dummy can be chosen arbitrarily; the conjunction forces the original disjunction
to hold.

For each source clause we therefore emit:
+ * one 3‑literal clause ``[a, b, c]``
+ * three pairs of 3‑literal clauses for the pairwise negative constraints,
+   each pair using its own fresh dummy variable.

The construction is polynomial in the size of the input (linear in the number
of source clauses) and preserves satisfiability: a satisfying assignment for
the source instance can be extended arbitrarily to the dummy variables, and any
assignment satisfying the produced 3‑SAT instance must satisfy the original
exactly‑one constraints.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SOURCE, TARGET


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``OneInThreeSat`` instance to an equivalent ``ThreeSat`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three positive integers each).

    Returns
    -------
    dict
        A ``ThreeSat`` instance satisfying the format requirements of
        ``ThreeSat.validate``.
    """

    # Validate the source instance – helpful for debugging and ensures we work
    # with well‑formed data.
    SOURCE.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # The target will contain the original variables plus a fresh dummy for each
    # pairwise negative clause (three per source clause).
    next_var: int = m + 1
    target_clauses: List[List[int]] = []

    for a, b, c in source_clauses:
        # At least one true.
        target_clauses.append([a, b, c])

        # Pairwise "not both true" constraints, each expanded with a dummy.
        for x, y in ((a, b), (a, c), (b, c)):
            d = next_var
            next_var += 1
            # (¬x ∨ ¬y ∨ d) and (¬x ∨ ¬y ∨ ¬d)
            target_clauses.append([-x, -y, d])
            target_clauses.append([-x, -y, -d])

    # Edge case: empty formula – just copy the number of variables.
    if not source_clauses:
        target_instance = {"num_vars": m, "clauses": []}
    else:
        target_instance = {"num_vars": next_var - 1, "clauses": target_clauses}

    # Ensure the produced instance conforms to the 3‑SAT specification.
    TARGET.validate(target_instance)
    return target_instance

