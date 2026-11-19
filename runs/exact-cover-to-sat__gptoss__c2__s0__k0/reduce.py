"""Reduction from Exact Cover to SAT.

Exact Cover instance format (as described in problems.py):
    {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are represented as signed integers: +v for variable v true, -v for false.
"""

def reduce(instance):
    """Transform an Exact Cover instance into an equivalent SAT instance.

    Parameters
    ----------
    instance: dict
        Exact Cover instance with keys "universe_size" and "sets".

    Returns
    -------
    dict
        SAT instance with keys "num_vars" and "clauses".
    """
    u = instance.get("universe_size", 0)
    sets = instance.get("sets", [])
    n = len(sets)  # number of variables (one per set)

    # Map each element to the list of set indices (1‑based) that contain it.
    elem_to_sets = {e: [] for e in range(u)}
    for idx, s in enumerate(sets, start=1):
        for e in s:
            # Assume input is well‑formed; ignore out‑of‑range elements.
            if 0 <= e < u:
                elem_to_sets[e].append(idx)

    clauses = []
    # For each element we need exactly one covering set.
    for e in range(u):
        covering = elem_to_sets[e]
        if not covering:
            # No set covers this element => unsatisfiable. Add an empty clause.
            clauses.append([])
            continue
        # At least one covering set must be chosen.
        clauses.append(covering[:])  # all positive literals
        # At most one covering set: for every pair, add (¬i ∨ ¬j).
        for i in range(len(covering)):
            for j in range(i + 1, len(covering)):
                clauses.append([-covering[i], -covering[j]])

    return {"num_vars": n, "clauses": clauses}

# If this file is executed directly, perform a simple sanity test.
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()
