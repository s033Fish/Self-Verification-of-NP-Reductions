"""Polynomial-time reduction from SAT to Independent Set.

Construction
------------
Given a CNF formula with clauses C_0, ..., C_{k-1}:

* Create one vertex for every literal occurrence in every clause.
* Add an edge between every pair of vertices that come from the same
  clause.  This makes each clause's vertices a clique, so an independent
  set contains at most one vertex per clause.
* Add an edge between every occurrence of a literal ``l`` and every
  occurrence of its complement ``-l``.  This prevents an independent set
  from selecting both ``v`` and ``-v``.
* Set ``k`` to the number of clauses.

Correctness
-----------
If the formula is satisfiable, pick one true literal per clause.  These
literals are pairwise non-complementary, so the corresponding vertices
form an independent set of size ``k``.

Conversely, an independent set of size at least ``k`` must contain exactly
one vertex from each of the ``k`` clause cliques (at most one per clique,
and there are only ``k`` cliques).  The selected literals cannot contain a
complementary pair, so setting exactly those literals to true is a
consistent assignment that satisfies every clause.

Edge cases
----------
* No clauses: ``k = 0`` and the empty graph is a yes-instance
  (``k <= 0`` is always yes).
* An empty clause contributes no vertices, so the maximum independent set
  has size at most ``k - 1 < k``; the instance is correctly no.
* Duplicate clauses and repeated literals are handled naturally because
  each occurrence gets its own vertex.
"""

from collections import defaultdict


def reduce(instance):
    """Reduce a SAT instance to an Independent Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence.
    literals = []            # vertex index -> literal
    clause_vertices = []     # clause index -> list of vertex indices
    for clause in clauses:
        indices = []
        for literal in clause:
            indices.append(len(literals))
            literals.append(literal)
        clause_vertices.append(indices)

    edges = set()

    # Edges inside each clause (make every clause a clique).
    for indices in clause_vertices:
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                edges.add(frozenset((indices[i], indices[j])))

    # Edges between complementary literals.
    occurrences = defaultdict(list)
    for vertex, literal in enumerate(literals):
        occurrences[literal].append(vertex)

    for literal, vertices in occurrences.items():
        for other in occurrences.get(-literal, ()):
            for vertex in vertices:
                if vertex != other:
                    edges.add(frozenset((vertex, other)))

    n = len(literals)
    k = len(clauses)

    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": k,
    }
