#!/usr/bin/env python3
"""Reduction from Vertex Cover to Independent Set.

Given an instance of Vertex Cover (graph G with n vertices, edge list, and integer k),
produce an instance of Independent Set on the same graph where the target size is
n - k.  A set C is a vertex cover of size ≤ k iff its complement V\C is an
independent set of size ≥ n - k.  This transformation runs in linear time.
"""

def reduce(instance):
    """Transform a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance : dict
        A dictionary with keys:
        - "n": number of vertices (int)
        - "edges": list of [u, v] pairs (list of lists)
        - "k": size bound for vertex cover (int)

    Returns
    -------
    dict
        An Independent Set instance with the same "n" and "edges", and
        "k" replaced by n - k.
    """
    n = instance["n"]
    k = instance["k"]
    # Compute the target k for Independent Set
    target_k = n - k
    # Return new instance preserving graph structure
    return {"n": n, "edges": list(instance["edges"]), "k": target_k}

# If this file is executed directly, perform a simple self-test.
if __name__ == "__main__":
    # Example: triangle graph, vertex cover k=2 => independent set k'=1
    example = {"n": 3, "edges": [[0,1],[1,2],[0,2]], "k": 2}
    print(reduce(example))
