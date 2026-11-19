"""Reduction from SAT to Independent Set.

Given a CNF formula instance (as defined in problems.py for SAT), produce an
instance of Independent Set such that the formula is satisfiable iff the graph
has an independent set of size at least k.

Standard reduction:
  * For each literal in each clause create a vertex.
  * Connect all vertices belonging to the same clause (forming a clique),
    ensuring at most one literal per clause can be chosen.
  * Connect vertices whose literals are complementary (v and -v) across
    different clauses, preventing contradictory assignments.
  * Set k = number of clauses.

Edge cases:
  * No clauses → formula is trivially satisfiable. Return a trivial
    Independent Set instance with k = 0 (always yes).
  * An empty clause → unsatisfiable. Return an instance with k > n, e.g.
    n = 0, k = 1, which is always a NO instance.
"""

def reduce(instance):
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance : dict
        SAT instance with keys "num_vars" and "clauses" as described.

    Returns
    -------
    dict
        Independent Set instance with keys "n", "edges", and "k".
    """
    num_vars = instance.get("num_vars")
    clauses = instance.get("clauses", [])

    # Edge case: formula with no clauses is always satisfiable.
    if len(clauses) == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Edge case: any empty clause makes the formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            # Return a NO instance: k > n.
            return {"n": 0, "edges": [], "k": 1}

    # General case.
    clause_count = len(clauses)
    # Assign a vertex id to each literal occurrence.
    # We'll store (clause_index, literal_index) -> vertex id.
    vertex_id = 0
    lit_vertices = []  # list of (clause_idx, literal, vertex_id)
    for ci, cl in enumerate(clauses):
        for lit in cl:
            lit_vertices.append((ci, lit, vertex_id))
            vertex_id += 1
    n = vertex_id

    # Build edge set.
    edge_set = set()
    # 1. Edges within each clause (clique).
    # Group vertices by clause.
    from collections import defaultdict
    clause_to_vertices = defaultdict(list)
    for ci, lit, vid in lit_vertices:
        clause_to_vertices[ci].append((lit, vid))
    for verts in clause_to_vertices.values():
        # add edges between all pairs
        L = len(verts)
        for i in range(L):
            for j in range(i + 1, L):
                u = verts[i][1]
                v = verts[j][1]
                if u > v:
                    u, v = v, u
                edge_set.add((u, v))

    # 2. Edges between complementary literals across different clauses.
    # For each pair of vertices from different clauses where lit1 == -lit2.
    # We'll map literal value to list of vertex ids per clause.
    # Simple O(N^2) check is fine.
    total = len(lit_vertices)
    for i in range(total):
        ci1, lit1, v1 = lit_vertices[i]
        for j in range(i + 1, total):
            ci2, lit2, v2 = lit_vertices[j]
            if ci1 == ci2:
                continue  # already handled within clause
            if lit1 == -lit2:
                u, v = v1, v2
                if u > v:
                    u, v = v, u
                edge_set.add((u, v))

    # Convert edge_set to required list format.
    edges = [[u, v] for (u, v) in edge_set]

    return {"n": n, "edges": edges, "k": clause_count}

# The module may be imported by the evaluation harness; no top-level code.
