"""Reduction from 3‑SAT to Dominating Set.

We construct a graph where each variable i creates three vertices:
  * true_i  (id 2*(i-1))   representing literal +i
  * false_i (id 2*(i-1)+1) representing literal -i
  * leaf_i  (id 2*m + (i-1)) connected to both true_i and false_i.
The leaf forces any dominating set of size ≤ m to include at least one of the two
literal vertices for each variable (otherwise leaf_i would be undominated).  The
budget k = m ensures we cannot afford to pick both literals for a variable,
because then some other variable's leaf would remain undominated.

For each clause we add a clause vertex (ids start after the 3*m variable‑related
vertices) and connect it to the three literal vertices appearing in the clause.
If the chosen literal satisfies the clause, the clause vertex is dominated; if
no chosen literal satisfies it, the clause vertex would need to be added to the
dominating set, exceeding the budget.

Thus the 3‑SAT formula is satisfiable iff the constructed graph has a dominating
set of size at most k = m.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A ``DominatingSet`` instance ``{"n": n, "edges": [...], "k": k}``.
    """
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex ids:
    #   true_i  = 2*(i-1)
    #   false_i = 2*(i-1)+1
    #   leaf_i  = 2*m + (i-1)
    # Clause vertices start after 3*m vertices.
    base_clause = 3 * m
    n = base_clause + len(clauses)
    edges: List[List[int]] = []

    # Variable gadget edges (leaf connected to both literals)
    for i in range(1, m + 1):
        true_id = 2 * (i - 1)
        false_id = true_id + 1
        leaf_id = 2 * m + (i - 1)
        edges.append([true_id, leaf_id])
        edges.append([false_id, leaf_id])
        # optional edge between true and false (does not affect correctness)
        edges.append([true_id, false_id])

    # Clause edges
    for idx, clause in enumerate(clauses):
        clause_vertex = base_clause + idx
        for lit in clause:
            var = abs(lit)
            lit_vertex = 2 * (var - 1) if lit > 0 else 2 * (var - 1) + 1
            edges.append([clause_vertex, lit_vertex])

    k = m
    result = {"n": n, "edges": edges, "k": k}
    DominatingSet.validate(result)
    return result

