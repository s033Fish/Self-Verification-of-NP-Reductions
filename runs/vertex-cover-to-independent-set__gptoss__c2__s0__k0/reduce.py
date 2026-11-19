import copy

def reduce(instance):
    """Reduce Vertex Cover instance to Independent Set instance.
    Given a graph G with n vertices and integer k, produce the same graph
    with parameter k' = n - k. A set S is a vertex cover of size ≤ k iff its
    complement V\S is an independent set of size ≥ n - k.
    """
    # Validate required keys exist
    n = instance.get("n")
    edges = instance.get("edges")
    k = instance.get("k")
    # Construct the target instance
    target_instance = {
        "n": n,
        "edges": copy.deepcopy(edges),  # edges unchanged
        "k": n - k
    }
    return target_instance

# If run as script, do a simple sanity check (optional)
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    print(json.dumps(reduce(data)))
