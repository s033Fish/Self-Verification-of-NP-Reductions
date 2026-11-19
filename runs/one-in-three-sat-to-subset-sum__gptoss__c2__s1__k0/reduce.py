"""Reduction from One-In-Three SAT to Subset Sum.

Source problem format (OneInThreeSat):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    - Variables are numbered 1..m.
    - Each clause contains exactly three distinct positive variable indices.
    - Duplicated clauses may appear.
    - A formula with no clauses is trivially satisfiable.

Target problem format (SubsetSum):
    {"numbers": [a1, a2, ...], "target": t}
    - All numbers are non‑negative integers.
    - The question is whether a sub‑multiset sums exactly to t.

Reduction idea:
    For each clause we allocate a distinct digit position in a mixed‑radix
    representation.  Choose a base B larger than the maximum possible sum
    in any digit; here B = 4 works because each clause contains at most
    three variables, so the digit sum never exceeds 3.

    For variable x_i we create a number whose B‑ary representation has a
    digit 1 in exactly those positions corresponding to clauses that contain
    x_i, and 0 elsewhere.  The target number has digit 1 in every clause
    position.  Selecting a subset of variable numbers that sums to the
    target forces each clause digit to sum to 1, i.e., exactly one variable
    in each clause is chosen true.

    This is a polynomial‑time many‑one reduction.
"""

def reduce(instance):
    """Reduce a OneInThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        {'num_vars': m, 'clauses': [[a, b, c], ...]}

    Returns
    -------
    dict
        {'numbers': [...], 'target': t} suitable for the SubsetSum solver.
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Base larger than the maximum sum per digit (max 3). Use 4.
    BASE = 4

    # Pre‑compute powers of BASE for each clause index.
    powers = [BASE ** i for i in range(num_clauses)]

    # Build numbers for each variable.
    numbers = []
    for var in range(1, m + 1):
        value = 0
        for idx, clause in enumerate(clauses):
            # clause is a list of three distinct variable indices.
            if var in clause:
                value += powers[idx]
        numbers.append(value)

    # Target has digit 1 in every clause position.
    target = sum(powers)

    return {"numbers": numbers, "target": target}

if __name__ == "__main__":
    # Simple self‑test (not used by the evaluation harness).
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
    sys.stdout.flush()
