import copy

def reduce(instance):
    """Reduce 1-in-3-SAT instance to 3-SAT instance.
    Input instance format: {"num_vars": m, "clauses": [[a,b,c], ...]}
    Output instance format: {"num_vars": M, "clauses": [[l1,l2,l3], ...]}
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    # If there are no clauses, return an empty 3-SAT instance with same num_vars
    if not clauses:
        return {"num_vars": m, "clauses": []}
    new_clauses = []
    next_var = m + 1  # next fresh variable index
    for clause in clauses:
        # clause is a list of three distinct positive integers
        a, b, c = clause
        # At least one true among a,b,c
        new_clauses.append([a, b, c])
        # At most one true: for each pair, enforce not both true
        for x, y in ((a, b), (a, c), (b, c)):
            p = next_var
            next_var += 1
            # Encode (¬x ∨ ¬y) using two 3-literal clauses with fresh p
            new_clauses.append([-x, -y, p])
            new_clauses.append([-x, -y, -p])
    return {"num_vars": next_var - 1, "clauses": new_clauses}

# If run as script, perform a simple sanity check (not required for the task)
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    out = reduce(data)
    json.dump(out, sys.stdout)
    sys.stdout.flush()
