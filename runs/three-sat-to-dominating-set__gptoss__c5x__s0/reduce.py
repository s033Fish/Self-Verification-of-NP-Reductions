"""Reduction from 3‑SAT to Dominating Set.

The source problem is :class:`ThreeSat` and the target is
``DominatingSet`` as defined in *problems.py*.

We implement the classic polynomial‑time reduction described in many
textbooks:

* For each variable *x_i* we create three vertices ``xi``, ``nxi`` and
  ``di`` forming a triangle.  Selecting ``xi`` (resp. ``nxi``) in the
  dominating set corresponds to setting the variable to *True* (resp.
  *False*).  Vertex ``di`` is only needed to force the choice of exactly
  one of ``xi`` or ``nxi`` – it will be dominated by the chosen literal.

* For each clause we create a single vertex ``cj``.  It is connected to
  the three literal vertices that appear in the clause.

* A special vertex ``u`` is added together with a pendant vertex ``p``
  that is adjacent only to ``u``.  This forces ``u`` to be part of any
  dominating set (otherwise ``p`` could not be dominated).  Vertex ``u``
  is also connected to every ``di`` so that ``di`` is dominated once ``u``
  is chosen.

If the 3‑SAT formula is satisfiable, we can build a dominating set of
size ``m + 1`` (``m`` = number of variables) consisting of ``u`` and the
chosen literal vertex for each variable.  Conversely, any dominating set
of size at most ``m + 1`` must contain ``u`` (to dominate ``p``) and can
use at most ``m`` additional vertices; these must be exactly one literal
per variable, which yields a satisfying assignment.

The reduction runs in time polynomial in the size of the formula.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`ThreeSat`.

    Returns
    -------
    dict
        An instance of ``DominatingSet`` with the property that the
        original formula is satisfiable iff the graph has a dominating
        set of size at most ``m + 1`` where ``m`` is the number of
        variables.
    """
    # Validate the source instance – this will raise if malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex allocation (sequential integer ids)
    # 0: universal vertex u
    # 1: pendant vertex p (only adjacent to u)
    next_id = 2
    var_pos: List[int] = []  # xi
    var_neg: List[int] = []  # nxi
    var_dummy: List[int] = []  # di
    for _ in range(m):
        xi = next_id
        nxi = next_id + 1
        di = next_id + 2
        var_pos.append(xi)
        var_neg.append(nxi)
        var_dummy.append(di)
        next_id += 3

    clause_vertices: List[int] = []
    for _ in clauses:
        clause_vertices.append(next_id)
        next_id += 1

    n_vertices = next_id

    edges_set: set[Tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            raise ValueError("self‑loops are not allowed")
        a, b = (u, v) if u < v else (v, u)
        edges_set.add((a, b))

    # pendant edge (u, p)
    u = 0
    p = 1
    add_edge(u, p)

    # variable gadgets: triangles (xi, nxi, di)
    for xi, nxi, di in zip(var_pos, var_neg, var_dummy):
        add_edge(xi, nxi)
        add_edge(xi, di)
        add_edge(nxi, di)
        # connect dummy to universal vertex to dominate it via u
        add_edge(u, di)

    # clause connections
    for cj, clause in zip(clause_vertices, clauses):
        for lit in clause:
            var = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                lit_vertex = var_pos[var]
            else:
                lit_vertex = var_neg[var]
            add_edge(cj, lit_vertex)

    # Convert edge set to required list format
    edges = [[u, v] for (u, v) in edges_set]

    # The budget k is m + 1 (universal vertex + one literal per variable)
    k = m + 1

    result = {"n": n_vertices, "edges": edges, "k": k}
    # Validate the target instance before returning.
    DominatingSet.validate(result)
    return result

