"""Reduction from Independent Set to Vertex Cover.

Given an instance of Independent Set with graph G = (V, E) and integer k,
we produce an instance of Vertex Cover on the same graph with integer k' = |V| - k.
The transformation is correct because a set S is independent of size >= k
iff its complement V\S is a vertex cover of size <= |V| - k.
"""

def reduce(instance):
    """Map an Independent Set instance to a Vertex Cover instance.

    Parameters:
        instance (dict): {'n': int, 'edges': [[u, v], ...], 'k': int}
    Returns:
        dict: {'n': int, 'edges': [[u, v], ...], 'k': int}
    """
    n = instance.get('n')
    edges = instance.get('edges')
    k = instance.get('k')
    # Compute the vertex cover size bound
    k_prime = n - k
    return {'n': n, 'edges': edges, 'k': k_prime}

# If run as script, perform a simple test (optional)
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
    sys.stdout.flush()
