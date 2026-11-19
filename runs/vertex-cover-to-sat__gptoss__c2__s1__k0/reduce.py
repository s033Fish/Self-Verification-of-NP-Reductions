import sys

def reduce(instance):
    n = instance.get('n')
    edges = instance.get('edges', [])
    k = instance.get('k')
    # Edge case: k < 0 -> always NO, produce unsatisfiable SAT (empty clause)
    if k is None:
        raise ValueError('Instance missing k')
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}
    # Number of variables: one per (vertex, slot) pair
    # If k == 0, there are no variables
    num_vars = n * max(k, 0)
    clauses = []
    # 1) At least one vertex in each slot j (1..k)
    for j in range(k):
        clause = []
        for i in range(n):
            var = i * k + (j + 1)  # variables are 1-indexed
            clause.append(var)
        if clause:
            clauses.append(clause)
    # 2) At most one vertex per slot: for each slot, pairwise exclusion
    for j in range(k):
        for i in range(n):
            vi = i * k + (j + 1)
            for ip in range(i + 1, n):
                vip = ip * k + (j + 1)
                clauses.append([-vi, -vip])
    # 3) Edge coverage: each edge must have at least one endpoint in some slot
    for (u, v) in edges:
        clause = []
        for j in range(k):
            clause.append(u * k + (j + 1))
            clause.append(v * k + (j + 1))
        # If k == 0 this clause will be empty, making the formula unsatisfiable when edges exist
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}

if __name__ == "__main__":
    # Simple driver to read JSON from stdin and output JSON to stdout
    import json
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()
