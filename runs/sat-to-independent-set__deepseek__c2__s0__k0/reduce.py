"""Polynomial-time reduction from SAT to Independent Set.

Construction
------------
Let the CNF formula have clauses C_1, ..., C_k over variables 1..m.

Create one vertex for every literal *occurrence* in the formula.  For a
clause C, the vertices corresponding to its literals form a clique (so an
independent set contains at most one vertex per clause).  Additionally,
connect every vertex labelled v with every vertex labelled -v (and vice
versa), so an independent set can never contain a literal together with
its negation.

Set k = number of clauses.

Correctness
-----------
If the formula is satisfiable, choose in each clause one true literal; the
chosen vertices are pairwise non-adjacent (one per clause, no complementary
pair), giving an independent set of size k.

Conversely, an independent set of size k must contain exactly one vertex
per clause (clauses are cliques and there are k clauses).  Assign each
variable the truth value that makes the chosen literal true; this is
consistent because no complementary pair is chosen, and every clause has a
true literal.  Hence the formula is satisfiable.

Edge cases
----------
* No clauses: n = 0, k = 0, so the answer is yes (k <= 0), matching SAT.
* An empty clause contributes no vertices, so n < k and the answer is no,
  matching the unsatisfiable empty clause.
* Repeated literals / repeated clauses simply create extra vertices and
  cliques; the argument above is unaffected.
"""

from collections import defaultdict


def reduce(instance):
    """Map a SAT instance to an Independent Set instance (yes iff yes)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence; remember the vertex span of each
    # clause so we can build the within-clause cliques.
    literals = []          # literals[i] is the literal at vertex i
    clause_spans = []      # (start, end) vertex indices for each clause
    for clause in clauses:
        start = len(literals)
        literals.extend(clause)
        clause_spans.append((start, len(literals)))

    n = len(literals)

    edges = set()  # frozenset({u, v}) to keep edges unique and undirected

    # Clique on the vertices of each clause.
    for start, end in clause_spans:
        for i in range(start, end):
            for j in range(i + 1, end):
                edges.add(frozenset((i, j)))

    # Edges between complementary literals (v and -v).
    by_literal = defaultdict(list)
    for index, literal in enumerate(literals):
        by_literal[literal].append(index)

    for literal, indices in by_literal.items():
        opposite = -literal
        if opposite not in by_literal:
            continue
        for i in indices:
            for j in by_literal[opposite]:
                edges.add(frozenset((i, j)))

    return {
        "n": n,
        "edges": [sorted(edge) for edge in edges],
        "k": len(clauses),
    }
