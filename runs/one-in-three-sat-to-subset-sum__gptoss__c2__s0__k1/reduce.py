"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem (OneInThreeSat) is defined as:
    instance = {"num_vars": m, "clauses": [[a, b, c], ...]}
    Each clause contains exactly three *different* positive variable indices
    (1‑based).  The formula is satisfiable iff there exists an assignment to the
    variables such that **exactly one** variable in every clause is true.

The target problem (SubsetSum) expects an instance of the form:
    {"numbers": [a1, a2, ...], "target": t}
    where the numbers are non‑negative integers and the question is whether a
    sub‑list sums to ``t``.

We use the classic base‑encoding reduction.  Choose a base ``B = 4`` – larger
than the maximum possible digit sum (which is 3 because each clause contains
three variables).  For each clause we allocate one digit position in this
base.  For each variable we create a number whose digit in position *j* (for
clause *j*) is ``1`` if the variable appears in that clause and ``0``
otherwise.  The target number has digit ``1`` in every clause position.  A
selection of variable‑numbers that sums to the target therefore picks exactly
one variable per clause (otherwise a digit would be 0 or ≥2, breaking the
equality).  Because the base is larger than any possible digit sum, no carries
occur, and the reduction is sound and complete.

The construction runs in time polynomial in the size of the input (O(m·n)
where ``n`` is the number of clauses) and produces only non‑negative integers.
Edge cases are handled automatically: an instance with no clauses yields an
empty list of clause positions, the target becomes ``0`` and the Subset‑Sum
instance is trivially a YES‑instance, matching the source problem definition.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of variable indices, 1‑based).

    Returns
    -------
    dict
        A SubsetSum instance ``{"numbers": [...], "target": t}`` satisfying the
        required equivalence.
    """

    num_vars: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Number of clauses determines the number of digit positions.
    n_clauses = len(clauses)

    # Base larger than the maximum possible digit sum (which is 3).
    BASE = 4

    # Pre‑compute powers of the base for each clause position.
    powers = [BASE ** i for i in range(n_clauses)]

    numbers: List[int] = []
    # Build a number for each variable.
    for var in range(1, num_vars + 1):
        value = 0
        for idx, clause in enumerate(clauses):
            if var in clause:
                value += powers[idx]
        # Omit zeroes – they are unnecessary for the SubsetSum instance.
        if value != 0:
            numbers.append(value)

    # Target has digit 1 in every clause position.
    target = sum(powers)

    return {"numbers": numbers, "target": target}

