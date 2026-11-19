"""Reduction from 3-SAT to Dominating Set.

Given a 3‑SAT instance with m variables and c clauses, we construct a graph G
with the following vertices and edges:

* For each variable i (1‑based) we create two vertices v_{i,T} and v_{i,F}.
  They are connected by an edge.  In any dominating set of size ≤ m we must
  pick at least one of them, which corresponds to fixing the truth value of
  variable i.
* For each clause j we create a clause vertex c_j.  It is connected to the
  three literal vertices that appear in the clause: to v_{i,T} if the literal
  is +i and to v_{i,F} if the literal is -i.

If the formula is satisfiable, picking for each variable the vertex that
represents the true literal yields a dominating set of size exactly m: each
clause vertex is adjacent to at least one chosen literal vertex, and every
variable vertex is either chosen or adjacent to its partner.
Conversely, any dominating set of size ≤ m must contain at least one of the
two vertices for each variable (otherwise the other would be undominated),
so it corresponds to a truth assignment.  To dominate each clause vertex,
the set must contain a literal vertex that satisfies the clause, giving a
satisfying assignment.

Thus the 3‑SAT instance is a YES instance iff the constructed graph has a
dominating set of size at most k = m.
"""

def reduce(instance):
    """Reduce a ThreeSat instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        A ThreeSat instance with keys "num_vars" (int) and "clauses"
        (list of list of ints).  Literals are encoded as +v for true and
        -v for false.

    Returns
    -------
    dict
        A DominatingSet instance with keys "n", "edges", "k".
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    c = len(clauses)

    # Vertex indexing:
    #   true literal of variable i (1‑based) -> 2*(i-1)
    #   false literal of variable i -> 2*(i-1) + 1
    # Clause vertices start at 2*m
    def true_vertex(i):
        return 2 * (i - 1)
    def false_vertex(i):
        return 2 * (i - 1) + 1

    # Build edges using a set to avoid duplicates.  Store each edge as a
    # sorted tuple (u, v) with u < v.
    edge_set = set()
    # Variable edges (pair each true/false vertex)
    for i in range(1, m + 1):
        u, v = true_vertex(i), false_vertex(i)
        if u != v:
            edge_set.add((min(u, v), max(u, v)))

    # Clause vertices and connections to literals
    for idx, clause in enumerate(clauses):
        clause_vertex = 2 * m + idx
        for lit in clause:
            var = abs(lit)
            if var == 0 or var > m:
                # Invalid literal according to spec; we simply ignore –
                # the validator of the source problem would reject such
                # instances, so this path will never be exercised.
                continue
            lit_vertex = true_vertex(var) if lit > 0 else false_vertex(var)
            edge_set.add((min(clause_vertex, lit_vertex), max(clause_vertex, lit_vertex)))

    # Convert edge set to the required list-of-lists format.
    edges = [[u, v] for (u, v) in sorted(edge_set)]

    n = 2 * m + c
    k = m
    return {"n": n, "edges": edges, "k": k}

if __name__ == "__main__":
    # Simple sanity test (not required for final submission)
    example = {"num_vars": 2, "clauses": [[1, -2, 2]]}
    print(reduce(example))
