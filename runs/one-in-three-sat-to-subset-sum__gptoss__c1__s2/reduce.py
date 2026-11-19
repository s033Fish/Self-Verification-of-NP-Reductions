"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem instance has the form:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause lists three *different* positive variable indices (1‑based).

The target Subset Sum instance must be a dictionary:
    {"numbers": [a1, a2, ...], "target": t}

We use a classic base‑B encoding to enforce that exactly one variable in each
clause is chosen.  For each clause we reserve a digit position in a base‑B
representation, where B is larger than the maximum possible digit sum (which
is 3 because each clause contains three variables).  Choosing a variable
corresponds to adding its number to the sum; the digit contributed by a
variable is 1 in each clause it appears in and 0 otherwise.  The target has a
digit value of 1 in every clause position, forcing exactly one true variable
per clause.

Implementation details:
  * Choose B = 4 (any integer > 3 works).
  * For variable i (1‑based) we create the number
        sum_{j where clause j contains i} B**j
    where j is the zero‑based index of the clause.
  * The target is sum_{j=0}^{C-1} B**j, where C is the number of clauses.
    This equals (B**C - 1) // (B - 1) for C > 0, and 0 when there are no clauses.

The reduction runs in time polynomial in the size of the input (O(m·C)).
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a One‑In‑Three SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "num_vars" (int) and "clauses" (list of
        three‑element lists of ints).

    Returns
    -------
    dict
        A Subset Sum instance with keys "numbers" (list of non‑negative
        integers) and "target" (int).
    """

    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    C = len(clauses)

    # Base larger than the maximum number of true variables that can appear in a
    # clause (which is 3).  Using 4 guarantees no carries between digit positions.
    B = 4

    # Pre‑compute powers of B for each clause index to avoid repeated exponentiation.
    powers = [pow(B, j) for j in range(C)]

    # Initialise numbers for each variable (1‑based indexing).
    numbers = [0] * m

    for j, clause in enumerate(clauses):
        weight = powers[j]
        for var in clause:
            # Variables are guaranteed to be in 1..m.
            numbers[var - 1] += weight

    # Compute target: digit 1 in every clause position.
    if C == 0:
        target = 0
    else:
        # (B**C - 1) // (B - 1) is the sum of a geometric series.
        target = (pow(B, C) - 1) // (B - 1)

    return {"numbers": numbers, "target": target}

