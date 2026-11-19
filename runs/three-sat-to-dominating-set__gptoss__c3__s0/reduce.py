"""Reduction from 3-SAT to Dominating Set.

The source problem is :class:`ThreeSat` (see ``problems.py``).  An instance
has the form ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
literal is an integer ``+v`` (variable *v* is true) or ``-v`` (variable *v*
is false).

The target problem is :class:`DominatingSet`.  An instance is a simple undirected
graph together with an integer ``k`` and asks whether the graph has a dominating
set of size at most ``k``.

The classic polynomial‑time reduction works as follows.

* For each variable ``x_i`` (``i`` from ``1`` to ``m``) we create two vertices:
  ``T_i`` representing ``x_i = True`` and ``F_i`` representing ``x_i = False``.
  They are connected by an edge, so any dominating set must contain at least one
  of the two vertices – this encodes the choice of a truth value.
* For each clause ``C_j`` we create a clause vertex ``C_j``.  It is connected to
  the three literal vertices that would satisfy the clause: if the literal is
  ``+i`` we connect to ``T_i``; if it is ``-i`` we connect to ``F_i``.
* No other edges are added.

With this construction a dominating set of size ``m`` exists **iff** the 3‑SAT
formula is satisfiable: pick exactly one vertex from each variable pair according
to a truth assignment; the clause vertices are dominated because each clause has
at least one satisfied literal, whose corresponding vertex is in the set.

The reduction runs in time linear in the size of the formula, which is
polynomial.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes for validation and reference.
from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` specification.

    Returns
    -------
    dict
        An instance of ``DominatingSet``.  The number of vertices is
        ``2 * m + n`` where ``m`` is the number of variables and ``n`` the number
        of clauses.  ``k`` is set to ``m``.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input is malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    n: int = len(clauses)

    # Vertex numbering:
    #   0,1   -> variable 1 (0 = true, 1 = false)
    #   2,3   -> variable 2, etc.
    #   2*m .. 2*m + n - 1 -> clause vertices.
    edges: List[List[int]] = []

    # Variable gadget: connect the true/false vertices of each variable.
    for i in range(m):
        true_v = 2 * i
        false_v = true_v + 1
        edges.append([true_v, false_v])

    # Clause vertices and their connections to the appropriate literal vertices.
    for j, clause in enumerate(clauses):
        clause_v = 2 * m + j
        for lit in clause:
            var = abs(lit)
            # Defensive: the validation already guarantees 1 <= var <= m.
            if not (1 <= var <= m):
                continue
            if lit > 0:
                lit_v = 2 * (var - 1)  # true vertex for variable var
            else:
                lit_v = 2 * (var - 1) + 1  # false vertex for variable var
            edges.append([clause_v, lit_v])

    total_vertices = 2 * m + n
    k = m  # one vertex per variable is sufficient and necessary.

    # Assemble the target instance.
    target_instance = {"n": total_vertices, "edges": edges, "k": k}
    # Validate the produced instance for sanity (optional but helpful).
    DominatingSet.validate(target_instance)
    return target_instance

