"""Reduction from OneInThreeSat to SubsetSum.

Given an instance of OneInThreeSat with m variables and a list of clauses (each a list of three distinct variable indices),
we construct a Subset Sum instance as follows.

For each variable i we create a number whose base‑4 representation has a 1 in the digit corresponding to each clause that contains i,
and 0 elsewhere.  The target number has a 1 in every clause digit.  Because the base (4) exceeds the maximum possible sum per digit (3),
no carries occur, so a subset of variable‑numbers sums to the target exactly when exactly one variable in each clause is chosen
(i.e., set to true).  Selecting a variable's number corresponds to assigning that variable true; not selecting it corresponds to false.

This reduction runs in time polynomial in the size of the OneInThreeSat instance.
"""

def reduce(instance):
    """Reduce a OneInThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "num_vars" (int) and "clauses" (list of list of ints).

    Returns
    -------
    dict
        A SubsetSum instance with keys "numbers" (list of non‑negative ints) and "target" (int).
    """
    # Base larger than the maximum number of true literals per clause (3).
    BASE = 4

    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    c = len(clauses)

    # Compute target = sum_{j=0}^{c-1} BASE**j, which has a 1 in each clause digit.
    target = 0
    for j in range(c):
        target += BASE ** j

    # Build mapping from variable to clause indices it appears in.
    var_to_clauses = {i: [] for i in range(1, m + 1)}
    for idx, clause in enumerate(clauses):
        for var in clause:
            var_to_clauses[var].append(idx)

    numbers = []
    for var in range(1, m + 1):
        num = 0
        for idx in var_to_clauses[var]:
            num += BASE ** idx
        numbers.append(num)

    return {"numbers": numbers, "target": target}

