"""Reduction from 3‑SAT to Dominating Set.

The source problem is :class:`ThreeSat` (as defined in ``problems.py``) and
the target problem is :class:`DominatingSet`.  Both classes provide a
``validate`` method that checks the instance format – we call this to ensure
that the input is well‑formed and to make the reduction robust.

The construction is a classic polynomial‑time reduction:

* For each variable ``x_i`` we create two vertices ``T_i`` (true) and ``F_i``
  (false) and connect them with an edge.  Selecting exactly one of the two
  vertices dominates both vertices of the variable gadget.
* For each clause ``C_j`` we create a vertex ``C_j`` and connect it to the
  literal‑vertices that satisfy the clause.  If a clause is satisfied by the
  chosen literal vertices, the clause vertex is dominated; otherwise it would
  need to be placed in the dominating set itself.

We set the budget ``k`` of the Dominating‑Set instance to ``num_vars``.  A
dominating set of size ``≤ k`` therefore must consist solely of one vertex per
variable gadget.  Such a set exists iff the original 3‑SAT formula is
 satisfiable – exactly the condition we need for a correct reduction.

The reduction runs in time ``O(num_vars + num_clauses)`` and produces a
simple undirected graph without parallel edges or self‑loops, satisfying the
validation rules of ``DominatingSet``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a ``ThreeSat`` instance.  It must contain
        the keys ``"num_vars"`` and ``"clauses"`` as described in the
        problem statement.

    Returns
    -------
    dict
        A dictionary representing a ``DominatingSet`` instance with keys
        ``"n"``, ``"edges"`` and ``"k"``.
    """
    # Validate the source instance – raises InvalidInstance on bad input.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]  # number of variables
    clauses: List[List[int]] = instance["clauses"]

    # Vertex layout:
    #   0 .. 2*m-1   – literal vertices (even = true, odd = false)
    #   2*m .. 2*m+len(clauses)-1 – clause vertices
    n_vertices = 2 * m + len(clauses)
    edges: List[List[int]] = []

    # Variable gadget edges (Ti – Fi)
    for i in range(m):
        true_v = 2 * i
        false_v = true_v + 1
        edges.append([true_v, false_v])

    # Clause‑literal edges
    for j, clause in enumerate(clauses):
        clause_v = 2 * m + j
        for lit in clause:
            var = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                literal_v = 2 * var  # true vertex
            else:
                literal_v = 2 * var + 1  # false vertex
            edges.append([clause_v, literal_v])

    # The budget k is exactly the number of variables.
    k = m

    result: Dict[str, Any] = {"n": n_vertices, "edges": edges, "k": k}
    # Validate the produced target instance before returning.
    DominatingSet.validate(result)
    return result

