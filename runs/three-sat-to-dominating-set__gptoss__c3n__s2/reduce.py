"""Reduction from 3‑SAT to Dominating Set.

The source problem is :class:`ThreeSat` defined in ``problems.py``.  An
instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each literal is an integer ``+v`` (variable *v* set to true) or ``-v``
(variable *v* set to false).  The target problem is :class:`DominatingSet`
with instance ``{"n": n, "edges": [[u, v], ...], "k": k}``.

We implement the classic polynomial‑time reduction used in textbooks:

* For each variable ``i`` (1‑based) we create two vertices ``t_i`` and ``f_i``
  representing the truth assignment of the variable.  An edge connects them.
* For each clause ``C_j`` we create a clause vertex ``c_j``.
* ``c_j`` is connected to the literal vertex that would satisfy the literal:
  a positive literal ``+i`` connects to ``t_i`` and a negative literal ``-i``
  connects to ``f_i``.
* No other edges are added.

Let ``m`` be the number of variables and ``c`` the number of clauses.  The
constructed graph has ``n = 2*m + c`` vertices.  We set ``k = m + c``.

Why does this work?
--------------------
* In any dominating set of size at most ``m + c`` at least one of ``t_i`` or
  ``f_i`` must be selected for each variable – otherwise the two vertices of
  that variable would remain undominated (they are only adjacent to each
  other).  Selecting both would waste a slot, so an optimal set will contain
  exactly one of the pair.
* A clause vertex ``c_j`` is dominated either by a selected literal vertex
  (meaning the clause is satisfied) or by selecting ``c_j`` itself.  Because
  we have exactly ``c`` additional slots beyond the ``m`` variable slots, we
  can afford to select a clause vertex only when the clause is not satisfied.
* Consequently a dominating set of size ``m + c`` exists iff the original
  formula is satisfiable.

The ``reduce`` function below follows this construction.  It validates the
source instance using :class:`ThreeSat.validate` and returns a dictionary
compatible with :class:`DominatingSet.validate`.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as described in the
        ``ThreeSat`` class docstring.

    Returns
    -------
    dict
        An instance of the ``DominatingSet`` problem.
    """
    # Validate the source instance – will raise InvalidInstance on error.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Vertex indexing:
    #   true literal of variable i (1‑based) -> 2*(i-1)
    #   false literal of variable i               -> 2*(i-1) + 1
    #   clause j (0‑based)                        -> 2*m + j
    n = 2 * m + c
    edges: List[List[int]] = []

    # Variable edges (t_i, f_i)
    for i in range(1, m + 1):
        t = 2 * (i - 1)
        f = t + 1
        edges.append([t, f])

    # Clause edges to the appropriate literal vertices
    for j, clause in enumerate(clauses):
        clause_vertex = 2 * m + j
        for lit in clause:
            var = abs(lit)
            # Determine which literal vertex the clause connects to.
            if lit > 0:
                literal_vertex = 2 * (var - 1)  # true vertex
            else:
                literal_vertex = 2 * (var - 1) + 1  # false vertex
            edges.append([clause_vertex, literal_vertex])

    k = m + c
    result: Dict[str, Any] = {"n": n, "edges": edges, "k": k}
    # Validate the target instance to guarantee correctness of the format.
    DominatingSet.validate(result)
    return result

