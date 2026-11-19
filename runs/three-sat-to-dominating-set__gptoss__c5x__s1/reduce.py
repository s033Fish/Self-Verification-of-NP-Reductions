"""Reduction from 3-SAT to Dominating Set.

The source problem is :class:`ThreeSat` defined in ``problems.py``.  An
instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each literal is an integer ``+v`` (variable ``v`` is true) or ``-v``
(variable ``v`` is false).

The target problem is :class:`DominatingSet`.  An instance is a dictionary
``{"n": n, "edges": [[u, v], ...], "k": k}``.

We construct a graph that has a dominating set of size at most ``m`` (the
number of variables) **iff** the 3‑SAT formula is satisfiable.

Construction (standard textbook reduction):

* For each variable ``i`` (1‑based) create two vertices ``i_T`` and ``i_F``
  representing the literal ``i`` being true or false.  Add an edge between
  them – picking either vertex dominates both.
* For each clause ``C_j`` create a clause vertex ``c_j``.  Connect ``c_j``
  to the three literal vertices that would satisfy the clause.  For a
  literal ``+i`` we connect to ``i_T``; for ``-i`` we connect to ``i_F``.
* No other edges are added.

Set ``k = m``.  If the formula is satisfiable we can pick exactly one vertex
per variable – the one corresponding to a satisfying assignment – and all
clause vertices are adjacent to at least one chosen vertex, giving a
dominating set of size ``m``.  Conversely, any dominating set of size ``m``
must contain exactly one of the two vertices for each variable (otherwise we
would need more than ``m`` vertices to dominate the isolated clause vertices).
If the formula is unsatisfiable, at least one clause vertex is not adjacent
to a selected literal vertex, so that clause vertex itself must be added to
the dominating set, forcing the size to be greater than ``m``.

The reduction runs in time polynomial in the size of the formula.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the :class:`ThreeSat` format.

    Returns
    -------
    dict
        A dictionary adhering to the :class:`DominatingSet` format such that
        the answer to the returned instance is *yes* exactly when the answer
        to ``instance`` is *yes*.
    """
    # Validate the source instance (will raise if malformed).
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex indexing:
    #   for variable i (1‑based) we assign:
    #       true vertex  = 2*(i-1)
    #       false vertex = 2*(i-1) + 1
    #   clause vertices start after the variable vertices.
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # Edge between true and false vertex of each variable.
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Add clause vertices and connect them to the appropriate literal vertices.
    clause_offset = 2 * m  # first clause vertex index
    for idx, clause in enumerate(clauses):
        clause_vertex = clause_offset + idx
        for lit in clause:
            var = abs(lit)
            if lit > 0:
                literal_vertex = var_true(var)
            else:
                literal_vertex = var_false(var)
            edges.append([clause_vertex, literal_vertex])

    n = clause_offset + len(clauses)
    k = m  # as argued in the docstring

    result = {"n": n, "edges": edges, "k": k}
    # Validate the target instance before returning.
    DominatingSet.validate(result)
    return result

