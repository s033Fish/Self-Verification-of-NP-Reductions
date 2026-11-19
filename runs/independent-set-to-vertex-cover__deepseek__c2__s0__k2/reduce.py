def reduce(instance):
    """Reduce Independent Set to Vertex Cover.

    A set S is independent in G if and only if its complement V \ S is a
    vertex cover of G.  Therefore G has an independent set of size at
    least k if and only if G has a vertex cover of size at most n - k.
    """
    n = instance["n"]
    return {
        "n": n,
        "edges": [list(edge) for edge in instance["edges"]],
        "k": n - instance["k"],
    }
