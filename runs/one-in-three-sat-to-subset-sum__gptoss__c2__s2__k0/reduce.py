"""Reduction from OneInThreeSat to SubsetSum.

Given an instance of 1-in-3 SAT with m variables and a list of clauses
(each clause is a list of three distinct variable indices), we construct a
Subset Sum instance.

For each variable i we create a number N_i whose base‑B representation has a
1 in the digit corresponding to each clause that contains i, and 0 otherwise.
We choose B = 4, which is larger than the maximum possible sum (3) in any
clause, so that carries never occur.

The target number T has a 1 in every clause position. Selecting a subset of
the N_i numbers sums to T exactly when each clause receives exactly one
true variable.
"""

def reduce(instance):
    # instance: {'num_vars': m, 'clauses': [[a,b,c], ...]}
    m = instance.get('num_vars', 0)
    clauses = instance.get('clauses', [])
    C = len(clauses)
    B = 4  # base larger than max literals per clause (3)

    # Map each clause to its index
    # Build for each variable the sum of B**clause_index where it appears
    var_numbers = [0] * (m + 1)  # 1-indexed
    for idx, clause in enumerate(clauses):
        power = B ** idx
        for var in clause:
            if 1 <= var <= m:
                var_numbers[var] += power
            else:
                # variable out of range – ignore (validation elsewhere)
                pass
    # Create list of numbers for all variables (including those never used)
    numbers = [var_numbers[i] for i in range(1, m + 1)]
    # Target has a 1 in each clause position
    target = sum(B ** idx for idx in range(C))
    return {"numbers": numbers, "target": target}

# If run as a script, allow simple manual testing
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()
