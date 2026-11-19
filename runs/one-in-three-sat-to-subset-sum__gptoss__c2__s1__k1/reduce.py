"""Reduction from OneInThreeSat to SubsetSum.

The source problem (OneInThreeSat) instance format:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
Each clause contains three distinct positive variable indices (1‑based).
The question is whether there exists an assignment to the m variables such that
exactly one variable in each clause is true.

The target problem (SubsetSum) instance format:
    {"numbers": [a1, a2, ...], "target": t}
All numbers are non‑negative integers; the target may be any integer.
The question is whether a sub‑list of the numbers sums to exactly t.

The reduction encodes each variable with two numbers, representing the choice
of setting the variable to True or False.  Digits are interpreted in a fixed
base B > 3 (we use B = 4).  The integer representation consists of a digit for
every clause followed by a digit for every variable.

* Clause digits (positions 0 … C‑1):
    - If a variable appears in clause j and we choose the *True* number for
      that variable, the digit at position j is 1; otherwise it is 0.
    - The target requires digit 1 for each clause, enforcing that exactly one
      true variable contributes to each clause.
* Variable‑selection digits (positions C … C+m‑1):
    - Both the True and False numbers for variable v have a 1 in the digit
      corresponding to v.  The target also requires a 1 for each variable,
      forcing exactly one of the two numbers to be selected.

Thus any subset achieving the target corresponds to a satisfying assignment,
and any satisfying assignment yields a subset with the required sum.
"""

def reduce(instance):
    """Convert a OneInThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "num_vars" (int) and "clauses" (list of
        three‑element lists of ints).

    Returns
    -------
    dict
        A SubsetSum instance with keys "numbers" (list of ints) and
        "target" (int).
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    C = len(clauses)
    # Base larger than the maximum possible sum in any digit (max 3).
    B = 4

    # Map each variable to the list of clause indices it appears in.
    var_to_clauses = {v: [] for v in range(1, m + 1)}
    for idx, clause in enumerate(clauses):
        for v in clause:
            # Variables are guaranteed to be in 1..m.
            var_to_clauses[v].append(idx)

    numbers = []
    # For each variable create a True-number and a False-number.
    for v in range(1, m + 1):
        # ----- True assignment -----
        # Build the integer digit‑wise.
        true_val = 0
        # Clause contribution: 1 for each clause containing v.
        for clause_idx in var_to_clauses[v]:
            true_val += B ** clause_idx  # digit 1 at position clause_idx
        # Variable‑selection digit.
        true_val += B ** (C + v - 1)
        numbers.append(true_val)

        # ----- False assignment -----
        false_val = B ** (C + v - 1)  # only the variable‑selection digit
        numbers.append(false_val)

    # Construct target: digit 1 for each clause and for each variable.
    target = 0
    for i in range(C):
        target += B ** i
    for i in range(m):
        target += B ** (C + i)

    return {"numbers": numbers, "target": target}

if __name__ == "__main__":
    # Simple sanity check when run directly.
    import json, sys
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
