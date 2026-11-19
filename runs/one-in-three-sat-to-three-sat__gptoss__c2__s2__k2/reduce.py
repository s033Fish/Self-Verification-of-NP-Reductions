import copy

def reduce(instance):
    """Reduce 1-in-3-SAT instance to 3-SAT instance.
    instance: dict with keys 'num_vars' (int) and 'clauses' (list of [a,b,c])
    Returns dict with same keys, clauses are lists of three literals (int, sign indicates negation).
    """
    m = instance.get("num_vars", 0)
    source_clauses = instance.get("clauses", [])
    # If there are no clauses, simply return an empty 3-SAT instance with same num_vars.
    if not source_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses = []
    next_var = m + 1  # next fresh variable index
    for clause in source_clauses:
        if len(clause) != 3:
            # Defensive: skip malformed clause (should not happen per validation)
            continue
        a, b, c = clause
        # At least one true among a,b,c
        new_clauses.append([a, b, c])
        # At most one true: pairwise ¬x ∨ ¬y constraints
        pairs = [(a, b), (a, c), (b, c)]
        for x, y in pairs:
            aux = next_var
            next_var += 1
            # Encode (¬x ∨ ¬y) as two 3‑clauses using aux
            new_clauses.append([-x, -y, aux])
            new_clauses.append([-x, -y, -aux])
    return {"num_vars": next_var - 1, "clauses": new_clauses}

# The module only defines the reduce function; no execution on import.
