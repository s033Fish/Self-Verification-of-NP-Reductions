"""Reduction from 3‑SAT to Dominating Set.

The source problem is :class:`ThreeSat` defined in ``problems.py``.
The target problem is :class:`DominatingSet` defined in the same file.

For a formula with *m* variables and *c* clauses we build a graph with
``2*m + c`` vertices:

* For each variable ``i`` (1‑based) we create two vertices representing the
  literal ``i`` (true) and ``-i`` (false).  An edge connects the two vertices.
  Selecting exactly one of the two vertices in a dominating set corresponds to
  assigning a truth value to the variable.
* For each clause we create a single *clause vertex*.  It is adjacent to the
  three literal vertices that appear in the clause.

We set ``k = m``.  A dominating set of size at most ``m`` must contain exactly
one literal vertex for each variable (the variable edges guarantee that one
choice dominates both literal vertices).  The clause vertices are dominated
iff at least one of their neighbour literal vertices is chosen, i.e. the
corresponding clause is satisfied.  Hence the formula is satisfiable iff the
graph admits a dominating set of size ``≤ m``.

The reduction runs in time polynomial in the size of the formula.
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
        A dictionary adhering to the ``DominatingSet`` format.
    """
    # Validate the source instance (will raise if malformed).
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex numbering:
    #   true literal of variable i (1‑based) -> 2*(i-1)
    #   false literal of variable i          -> 2*(i-1) + 1
    #   clause j (0‑based)                   -> 2*m + j
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1
    clause_vertex = lambda j: 2 * m + j

    edges: List[List[int]] = []

    # Add edges between each pair of literal vertices for a variable.
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Add edges from each clause vertex to the three literals appearing in it.
    for j, clause in enumerate(clauses):
        cv = clause_vertex(j)
        for lit in clause:
            if lit > 0:
                edges.append([cv, var_true(lit)])
            else:
                edges.append([cv, var_false(-lit)])

    n = 2 * m + c
    k = m

    result = {"n": n, "edges": edges, "k": k}
    # Validate the produced target instance.
    DominatingSet.validate(result)
    return result

