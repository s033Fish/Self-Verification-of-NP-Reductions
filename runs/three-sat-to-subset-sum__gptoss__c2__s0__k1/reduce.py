import math

def reduce(instance):
    """Reduce a 3-SAT instance to a Subset Sum instance.
    The reduction uses binary encoding: each variable contributes a unique
    power of two, and each clause contributes a distinct higher-order power of two.
    For each variable we create two numbers (true/false). Selecting exactly one
    number per variable corresponds to an assignment. The clause bits are added
    to those numbers that make the clause true. The target requires exactly one
    variable bit and one clause bit for each clause, forcing the selection to
    correspond to a satisfying assignment.
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    k = len(clauses)

    # Preprocess: for each variable, collect clause indices where the literal appears.
    # Use 0-based indices for bits.
    var_true_clauses = {v: [] for v in range(1, m+1)}
    var_false_clauses = {v: [] for v in range(1, m+1)}
    for idx, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit)
            if lit > 0:
                var_true_clauses[var].append(idx)
            else:
                var_false_clauses[var].append(idx)

    numbers = []
    # For each variable, create true and false numbers.
    for v in range(1, m+1):
        var_bit = 1 << (v-1)  # unique bit for variable v
        # true assignment number
        true_val = var_bit
        for clause_idx in var_true_clauses[v]:
            clause_bit = 1 << (m + clause_idx)
            true_val += clause_bit
        numbers.append(true_val)
        # false assignment number
        false_val = var_bit
        for clause_idx in var_false_clauses[v]:
            clause_bit = 1 << (m + clause_idx)
            false_val += clause_bit
        numbers.append(false_val)

    # Target: sum of all variable bits and one clause bit per clause.
    target = 0
    for v in range(1, m+1):
        target += 1 << (v-1)
    for j in range(k):
        target += 1 << (m + j)

    return {"numbers": numbers, "target": target}

