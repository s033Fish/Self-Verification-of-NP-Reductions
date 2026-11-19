"""Reduction from OneInThreeSat to SubsetSum.

SOURCE format (OneInThreeSat):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    Variables are 1-indexed.

TARGET format (SubsetSum):
    {"numbers": [a1, a2, ...], "target": t}
"""

def reduce(instance):
    """Reduce a 1-in-3 SAT instance to a Subset Sum instance.

    The reduction uses a base B = k+1 where k is the number of clauses.
    For each variable i we create a number whose representation in base B has
    a digit 1 in each clause position where variable i appears, and 0 otherwise.
    The target number has digit 1 in every clause position, enforcing that the
    selected subset (the true variables) contributes exactly one per clause.
    Because B > 3, no carries occur, and the digitwise equality is equivalent
    to the 1‑in‑3 condition.
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    k = len(clauses)
    # Edge case: no clauses => always yes. Return empty numbers and target 0.
    if k == 0:
        return {"numbers": [], "target": 0}
    # Choose base larger than maximum possible sum per digit (which is 3).
    B = k + 1  # Since k >= 1, B >= 2 and > 3 when k >= 3. For k < 3, ensure >3.
    if B <= 3:
        B = 4
    # Build numbers for each variable.
    numbers = []
    # Precompute for each variable the set of clause indices it appears in.
    var_clause_indices = {i: [] for i in range(1, m + 1)}
    for idx, clause in enumerate(clauses):
        for var in clause:
            # Assuming input is valid (variables within 1..m)
            var_clause_indices[var].append(idx)
    for i in range(1, m + 1):
        coeff = 0
        for idx in var_clause_indices[i]:
            coeff += B ** idx
        numbers.append(coeff)
    # Target has digit 1 in each clause position.
    target = sum(B ** idx for idx in range(k))
    return {"numbers": numbers, "target": target}

# The module may be imported by the evaluation harness; no top‑level code.
