"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem (SAT) is defined in ``problems.py`` with the following
instance format:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where a *literal* is an integer ``+v`` (variable ``v`` is true) or ``-v``
(variable ``v`` is false).  A clause is a list of literals and may be empty.

The target problem (Clique) expects an instance of the form:

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0`` through ``n-1`` and ``k`` is the required
clique size.

The classic polynomial‑time reduction creates a vertex for every literal in
each clause.  Two vertices are connected by an edge if they belong to
different clauses *and* they are not contradictory, i.e. they do not refer to
the same variable with opposite signs.  A satisfying assignment exists iff the
graph contains a clique of size equal to the number of clauses.

Edge cases handled:
* **No clauses** – the SAT instance is trivially satisfiable.  We return a
  Clique instance with ``k = 0`` (always a yes‑instance) and ``n = 0``.
* **Empty clause** – such a clause contributes no vertices, making it
  impossible to pick one vertex per clause, so the resulting graph cannot have
  a clique of size ``k``.  This correctly mirrors the unsatisfiable nature of
  the SAT instance.

The implementation runs in polynomial time with respect to the total number
of literals across all clauses.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A SAT instance following the format described above.

    Returns
    -------
    dict
        A Clique instance such that the Clique instance is a yes‑instance
        iff the original SAT instance is satisfiable.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses – SAT is trivially satisfiable.  Any graph with
    # k <= 0 is a yes‑instance for Clique, so we return the minimal graph.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build a list of vertices.  Each vertex corresponds to a literal inside a
    # specific clause.  We store (clause_index, literal) for later reference.
    vertices: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    edges: List[List[int]] = []

    # Helper to extract variable id and sign from a literal.
    def var_sign(lit: int) -> tuple[int, bool]:
        return abs(lit), lit > 0

    # Add edges between vertices from different clauses that are not
    # contradictory.
    for i in range(n):
        ci, lit_i = vertices[i]
        var_i, sign_i = var_sign(lit_i)
        for j in range(i + 1, n):
            cj, lit_j = vertices[j]
            if ci == cj:
                continue  # same clause – cannot be both in a clique
            var_j, sign_j = var_sign(lit_j)
            # Contradiction: same variable with opposite truth values.
            if var_i == var_j and sign_i != sign_j:
                continue
            edges.append([i, j])

    # The required clique size is the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

