import itertools

def reduce(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    # Edge cases
    if k <= 0:
        # Always yes: produce empty formula (no clauses)
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Yes iff n >= 1, but if n == 0 then no. Handle n==0.
        if n >= 1:
            return {"num_vars": 1, "clauses": [[1]]}  # single variable true
        else:
            return {"num_vars": 1, "clauses": [[]]}  # unsat
    if k > n:
        # Always no: produce unsatisfiable formula, e.g., empty clause
        return {"num_vars": 1, "clauses": [[]]}
    # General case
    # Variables x_{i,v} where i in [0,k-1], v in [0,n-1]
    # Map to SAT variable index (1-based)
    def var_index(i, v):
        return i * n + v + 1
    clauses = []
    # 1) Each position i must have at least one vertex
    for i in range(k):
        clause = [var_index(i, v) for v in range(n)]
        clauses.append(clause)
    # 2) No vertex appears in two positions
    for v in range(n):
        for i in range(k):
            for j in range(i+1, k):
                clauses.append([-var_index(i, v), -var_index(j, v)])
    # 3) Non-edges cannot both be selected for different positions
    # Precompute non-edges (u,v) with u != v and not in edges
    non_edges = []
    for u in range(n):
        for v in range(u+1, n):
            if (u, v) not in edges:
                non_edges.append((u, v))
    for i in range(k):
        for j in range(i+1, k):
            for (u, v) in non_edges:
                # u at position i and v at position j cannot both be chosen
                clauses.append([-var_index(i, u), -var_index(j, v)])
                # v at position i and u at position j cannot both be chosen
                clauses.append([-var_index(i, v), -var_index(j, u)])
    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

# If run as script, allow simple testing
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    out = reduce(data)
    json.dump(out, sys.stdout)
