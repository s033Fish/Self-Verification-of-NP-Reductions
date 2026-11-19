"""Reduction from Hamiltonian Path (SOURCE) to Hamiltonian Cycle (TARGET).

The source instance format:
    {"n": n, "edges": [[u, v], ...]}
The target instance format is the same.

The reduction works as follows:
* For n >= 3, add a new vertex (indexed n) and connect it to every
  original vertex.  The resulting graph has a Hamiltonian cycle iff the
  original graph has a Hamiltonian path.
* For n <= 2 we handle the cases directly, because the simple
  construction above would not preserve correctness for these tiny
  graphs.  We compute the answer for the Hamiltonian Path instance (which
  is trivial for n <= 2) and then output a target instance that is a YES
  instance (a triangle) or a NO instance (a graph with two isolated
  vertices) accordingly.

The function runs in polynomial time.
"""

def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Helper to check existence of an undirected edge
    def has_edge(u, v):
        for e in edges:
            if (e[0] == u and e[1] == v) or (e[0] == v and e[1] == u):
                return True
        return False

    # Small n handling (n <= 2)
    if n <= 2:
        # Determine answer for Hamiltonian Path directly
        if n == 0:
            yes = False
        elif n == 1:
            yes = True
        else:  # n == 2
            yes = has_edge(0, 1)
        if yes:
            # Return a YES instance for Hamiltonian Cycle: a triangle
            return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}
        else:
            # Return a NO instance for Hamiltonian Cycle: two isolated vertices
            return {"n": 2, "edges": []}

    # General case: n >= 3
    new_n = n + 1  # index of the added vertex
    # Copy original edges
    new_edges = [list(e) for e in edges]
    # Connect the new vertex to every original vertex
    for v in range(n):
        new_edges.append([v, new_n - 1])
    return {"n": new_n, "edges": new_edges}

# If this file is run directly, perform a simple self‑test (optional)
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
    sys.stdout.write("\n")

