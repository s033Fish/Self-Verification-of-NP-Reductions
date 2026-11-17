"""Reduction from 1-in-3-SAT to 3-SAT.

The source problem (OneInThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *positive* variables.  An assignment is a
solution iff **exactly one** variable in each clause is true.

The target problem (ThreeSat) expects a standard 3‑CNF where each clause has
exactly three *distinct* literals (positive or negative).  A clause is
satisfied if at least one literal is true.

For a clause ``(a ∨ b ∨ c)`` the “exactly‑one” condition can be expressed as

    (a ∨ b ∨ c)                # at least one is true
    (¬a ∨ ¬b) ∧ (¬a ∨ ¬c) ∧ (¬b ∨ ¬c)   # no two are true together

The three binary clauses are not directly allowed in 3‑SAT because each
clause must have three literals.  We introduce a fresh auxiliary variable
``p`` for each binary clause and replace ``(¬x ∨ ¬y)`` with the pair of
clauses ``(¬x ∨ ¬y ∨ p)`` and ``(¬x ∨ ¬y ∨ ¬p)``.  Together they are
equivalent to the original binary clause regardless of the value of ``p``.

Thus each original clause yields seven 3‑literal clauses and three new
variables.  The construction is clearly polynomial in the size of the input.

The ``reduce`` function implements this transformation.  It validates the
input using the source problem's ``validate`` method and returns a valid
target instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SOURCE, TARGET


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the source format.

    Returns
    -------
    dict
        A dictionary adhering to the target format such that the target is
        satisfiable iff the source instance is satisfiable.
    """
    # Validate the source instance – this will raise InvalidInstance on error.
    SOURCE.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Prepare the output structure.
    new_clauses: List[List[int]] = []
    next_var = m + 1  # first fresh variable index

    for clause in clauses:
        a, b, c = clause  # each clause has exactly three distinct positive ints
        # 1. At least one true.
        new_clauses.append([a, b, c])

        # Helper to add the padded binary clause using a fresh variable.
        def add_pair(x: int, y: int) -> None:
            nonlocal next_var
            p = next_var
            next_var += 1
            # (¬x ∨ ¬y)  =>  (¬x ∨ ¬y ∨ p) ∧ (¬x ∨ ¬y ∨ ¬p)
            new_clauses.append([-x, -y, p])
            new_clauses.append([-x, -y, -p])

        # 2. No two true together – three pairs.
        add_pair(a, b)
        add_pair(a, c)
        add_pair(b, c)

    # The total number of variables is the original plus all fresh ones introduced.
    total_vars = next_var - 1
    # Build the target instance.
    target_instance: Dict[str, Any] = {"num_vars": total_vars, "clauses": new_clauses}
    # Validate the constructed instance to catch programming mistakes.
    TARGET.validate(target_instance)
    return target_instance

