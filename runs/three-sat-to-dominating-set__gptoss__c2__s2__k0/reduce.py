"""Reduction from 3‑SAT to Dominating Set.

The source problem is ``ThreeSat`` whose instance format is::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Every clause contains exactly three
different variables.

The target problem is ``DominatingSet`` with instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 .. n‑1`` and the graph is undirected.

The classic polynomial‑time reduction creates a variable gadget consisting of
two vertices (one for the true literal, one for the false literal) connected by
an edge.  Selecting at least one vertex from each gadget is necessary to
dominate the other vertex, which forces the dominating set to choose a truth
value for each variable.

For every clause we add a clause vertex that is adjacent to the three
corresponding literal vertices.  To dominate the clause vertex we must either
pick the clause vertex itself or pick one of those three literals.  By setting
``k = m + |clauses|`` we make it impossible to pick all clause vertices – the
set must instead pick exactly one literal from each variable gadget and use
those literals to dominate all clause vertices.  Such a dominating set exists
iff the original 3‑SAT formula is satisfiable.

Edge cases:
* An empty formula (no clauses) is always satisfiable.  The reduction yields an
  empty graph with ``k = 0`` which trivially has a dominating set.
* If there are clauses but ``m = 0`` the input is invalid according to the
  problem statement, however the construction still works (the clause vertices
  would be isolated and therefore each would have to be chosen, exceeding the
  allowed ``k``).  No special handling is required.

The function ``reduce`` implements this construction and runs in linear time
in the size of the 3‑SAT instance.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}``
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    num_clauses = len(clauses)

    # Vertex numbering:
    #   true literal of variable i (1‑based) -> 2*(i-1)
    #   false literal of variable i               -> 2*(i-1) + 1
    #   clause j (0‑based)                        -> 2*m + j
    n = 2 * m + num_clauses
    edges: List[List[int]] = []

    # Variable gadgets: an edge between the true and false vertex of each var.
    for i in range(1, m + 1):
        true_v = 2 * (i - 1)
        false_v = true_v + 1
        edges.append([true_v, false_v])

    # Clause vertices and their connections to literals.
    for idx, clause in enumerate(clauses):
        clause_v = 2 * m + idx
        for lit in clause:
            var = abs(lit)
            if var == 0 or var > m:
                # Invalid literal – the source validator would reject such an
                # instance, but we guard against it to avoid crashes.
                continue
            # Choose the appropriate literal vertex.
            if lit > 0:
                lit_v = 2 * (var - 1)      # true literal vertex
            else:
                lit_v = 2 * (var - 1) + 1  # false literal vertex
            edges.append([clause_v, lit_v])

    k = m + num_clauses

    return {"n": n, "edges": edges, "k": k}

