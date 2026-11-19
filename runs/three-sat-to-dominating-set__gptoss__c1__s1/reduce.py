"""Reduction from 3-SAT (SOURCE) to Dominating Set (TARGET).

The source instance is a dictionary with keys:
    - "num_vars": number of variables *m*
    - "clauses": list of clauses, each a list of three integers
      representing literals (+v for true, -v for false).

The target instance must be a dictionary with keys:
    - "n": number of vertices
    - "edges": list of undirected edges ``[u, v]``
    - "k": size bound for the dominating set

We use the classic polynomial‑time reduction that forces any dominating set
of size *≤ m* to pick exactly one literal vertex for each variable.  The
construction is as follows (see e.g. Garey & Johnson, *Computers and
Intractability*):

* For each variable *i* (1‑based) create three vertices:
    - ``t_i``  (true literal)   index ``3*(i-1)``
    - ``f_i``  (false literal)  index ``3*(i-1)+1``
    - ``a_i``  (auxiliary)      index ``3*(i-1)+2``
  Connect them as a triangle: ``t_i‑f_i``, ``t_i‑a_i``, ``f_i‑a_i``.
  Selecting either ``t_i`` or ``f_i`` dominates the whole gadget, and any
  dominating set must contain at least one vertex from each gadget to dominate
  ``a_i``.

* For each clause *C_j* create a clause vertex ``c_j`` (index ``3*m + j``).
  Connect ``c_j`` to the three literal vertices that appear in the clause
  (positive literal → ``t_v``, negative literal → ``f_v``).

Set the budget ``k = m``.  Any dominating set of size at most ``m`` must pick
exactly one vertex from each variable gadget (otherwise it would need more
than ``m`` vertices).  Consequently every clause vertex must be adjacent to a
selected literal vertex, which is precisely a satisfying assignment.

The reduction runs in time linear in the size of the SAT instance and returns
an instance that satisfies the format required by ``DominatingSet``.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": m}``
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex indexing:
    #   true_i  = 3*i
    #   false_i = 3*i + 1
    #   aux_i   = 3*i + 2   (i is 0‑based for the loop)
    # Clause vertices start after the 3*m variable vertices.
    var_vertices = 3 * m
    clause_offset = var_vertices
    c = len(clauses)
    n = var_vertices + c

    edges: List[List[int]] = []

    # Variable gadgets – triangles.
    for i in range(m):
        true_v = 3 * i
        false_v = true_v + 1
        aux_v = true_v + 2
        edges.append([true_v, false_v])
        edges.append([true_v, aux_v])
        edges.append([false_v, aux_v])

    # Clause vertices connections to literal vertices.
    for j, clause in enumerate(clauses):
        clause_v = clause_offset + j
        for lit in clause:
            var = abs(lit) - 1  # 0‑based variable index
            if lit > 0:
                lit_v = 3 * var  # true vertex
            else:
                lit_v = 3 * var + 1  # false vertex
            edges.append([clause_v, lit_v])

    # The budget is exactly the number of variables.
    k = m

    return {"n": n, "edges": edges, "k": k}

