"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem (SAT) is defined in ``problems.py`` with the following
instance format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where a *literal* is an integer ``+v`` (variable *v* set to True) or ``-v``
(variable *v* set to False).  A clause may be empty, may contain duplicate
 literals, and may even contain both a literal and its negation.

The target problem (Clique) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

with vertices numbered ``0 .. n-1`` and an undirected edge list.  The answer
is *yes* iff the graph contains a clique of size **at least** ``k``.

The classic polynomial‑time reduction creates a vertex for every literal
occurring in a clause and connects two vertices with an edge iff they come
from *different* clauses and are not contradictory (i.e., they do not refer
to the same variable with opposite signs).  A selection of one vertex from
each clause that are pairwise adjacent corresponds exactly to a satisfying
assignment.

Edge‑case handling matches the specifications of both problems:

* If the SAT instance has **no clauses**, it is trivially satisfiable.  We
  output a Clique instance with ``k = 0`` (always a yes‑instance) and an
  empty graph.
* If any clause is empty, the SAT instance is unsatisfiable.  The reduction
  creates no vertex for that clause, so the resulting graph cannot contain a
  clique of size ``c`` (the number of clauses).  Consequently the Clique
  instance is a no‑instance, as required.

The function runs in time polynomial in the size of the SAT instance –
specifically ``O(V^2)`` where ``V`` is the total number of literal
occurrences, which is bounded by the input size.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        above.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": [...], "k": k}`` that is a
        yes‑instance iff the original SAT instance is satisfiable.
    """

    num_vars: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses: int = len(clauses)

    # Edge case: formula with no clauses – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build a vertex for each literal occurrence in each clause.
    # Store as (clause_index, literal) pairs.
    vertices: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n: int = len(vertices)
    edges: List[List[int]] = []
    # Add edges between vertices from different clauses that are not contradictory.
    for i in range(n):
        ci1, lit1 = vertices[i]
        var1 = abs(lit1)
        sign1 = lit1 > 0
        for j in range(i + 1, n):
            ci2, lit2 = vertices[j]
            if ci1 == ci2:
                # Vertices from the same clause cannot be both selected.
                continue
            var2 = abs(lit2)
            sign2 = lit2 > 0
            # Contradictory if same variable with opposite signs.
            if var1 == var2 and sign1 != sign2:
                continue
            edges.append([i, j])

    # The target clique size is the number of clauses.
    k: int = num_clauses
    return {"n": n, "edges": edges, "k": k}

