"""Reduction from 3‑SAT to Dominating Set.

The source problem (ThreeSat) is described in ``problems.py`` as a
dictionary with keys ``"num_vars"`` and ``"clauses"``.  Each clause is a
list of three literals where a literal is represented by an integer:
``+v`` means variable *v* is true, ``-v`` means variable *v* is false.

The target problem (DominatingSet) expects a graph given by the number
of vertices ``n``, a list of undirected edges ``edges`` (each edge is a
pair ``[u, v]`` with ``u != v``) and an integer ``k``.  The question is
whether the graph has a dominating set of size at most ``k``.

We implement the classic polynomial‑time many‑one reduction that encodes
assignments as a choice of exactly one vertex from each *variable pair*.

Construction
==============
* For each variable ``i`` (1‑based) we create two vertices:
  ``Ti`` (the literal *x_i*) and ``Fi`` (the literal *¬x_i*).  They are
  connected by an edge.  Selecting either ``Ti`` or ``Fi`` dominates the
  whole pair, so a dominating set of size ``m`` can contain at most one
  vertex from each pair.

* For each clause ``C_j`` we create a single clause vertex ``Cj``.  It is
  connected to the three literal vertices that appear in the clause.  If
  at least one of those literals is chosen in the dominating set, the
  clause vertex is adjacent to a chosen vertex, so it is dominated.  If
  none are chosen the only way to dominate ``Cj`` would be to include
  ``Cj`` itself, which would increase the size of the dominating set
  beyond ``m``.

With ``k = m`` (the number of variables) we obtain the following
equivalence:

*If the formula is satisfiable* – pick for each variable the vertex that
corresponds to the truth value in a satisfying assignment.  Exactly ``m``
vertices are chosen and every clause vertex is adjacent to at least one
chosen literal vertex, so the set dominates the whole graph.

*If the formula is unsatisfiable* – any set of at most ``m`` vertices can
choose at most one literal per variable.  Consequently there exists a
clause whose three literals are all false under this partial assignment;
its clause vertex is not dominated, and the set fails to be a dominating
set.  Any dominating set must therefore contain more than ``m`` vertices.

The reduction runs in time linear in the size of the 3‑SAT instance.
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
        ``{"n": n, "edges": [[u, v], ...], "k": k}`` suitable for the
        ``DominatingSet`` problem.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex numbering:
    #   For variable i (1‑based): true vertex = 2*(i-1), false vertex = 2*(i-1)+1
    #   Clause vertices start after the 2*m variable vertices.
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    clause_offset = 2 * m
    edges: List[List[int]] = []

    # Variable edges (Ti – Fi)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Clause vertices and connections to literals
    for idx, clause in enumerate(clauses):
        clause_vertex = clause_offset + idx
        for lit in clause:
            var = abs(lit)
            if var == 0 or var > m:
                # Defensive: ignore malformed literals; the validator will
                # catch invalid instances, but we keep the reduction robust.
                continue
            if lit > 0:
                lit_vertex = var_true(var)
            else:
                lit_vertex = var_false(var)
            edges.append([clause_vertex, lit_vertex])

    n = clause_offset + len(clauses)
    k = m
    return {"n": n, "edges": edges, "k": k}

