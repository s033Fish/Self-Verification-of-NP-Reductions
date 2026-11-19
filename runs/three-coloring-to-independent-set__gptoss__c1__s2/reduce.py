"""Reduction from 3-Coloring to Independent Set.

Source problem (ThreeColoring) instance format:
    {"n": n, "edges": [[u, v], ...]}
Target problem (IndependentSet) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction constructs a graph H where each vertex of the original graph
is represented by three vertices, one for each possible colour.  Edges are
added so that an independent set of size n in H corresponds exactly to a
proper 3‑colouring of the original graph.
"""

def reduce(instance):
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n" (int) and "edges" (list of [u, v]).

    Returns
    -------
    dict
        An IndependentSet instance with keys "n", "edges", and "k".
    """
    n = instance.get("n", 0)
    orig_edges = instance.get("edges", [])

    # New graph has 3 vertices per original vertex
    new_n = 3 * n
    edges = []
    # Helper to compute new vertex id for (v, colour)
    def vid(v, colour):
        return v * 3 + colour

    # Add edges making each triple of colour vertices a triangle (at most one colour per vertex)
    for v in range(n):
        a = vid(v, 0)
        b = vid(v, 1)
        c = vid(v, 2)
        edges.append([a, b])
        edges.append([a, c])
        edges.append([b, c])

    # For each original edge, forbid same colour on both endpoints
    for u, v in orig_edges:
        for colour in range(3):
            edges.append([vid(u, colour), vid(v, colour)])

    # k should be exactly n (pick one colour per original vertex)
    k = n
    return {"n": new_n, "edges": edges, "k": k}

# The module may be imported; expose reduce in __all__
__all__ = ["reduce"]
