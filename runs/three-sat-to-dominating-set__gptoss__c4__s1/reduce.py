"""Reduction from 3-SAT to Dominating Set.

The source problem is :class:`ThreeSat` defined in ``problems.py``.
The target problem is :class:`DominatingSet` also defined there.

We use a standard reduction that forces exactly one literal per variable to be
selected in any feasible dominating set of size ``m`` (the number of variables).
For each variable we create a triangle (three vertices) where selecting any two
vertices already dominates the whole triangle, but selecting only one does not.
Thus a minimum dominating set of size ``m`` must pick exactly one vertex from each
triangle, which we interpret as the truth assignment (choose the ``true`` vertex
or the ``false`` vertex). The third vertex of the triangle is a dummy that will
never be chosen in an optimal set of size ``m``.

Each clause gets a clause vertex connected to the three literal vertices that
would satisfy the clause. If the assignment satisfies the clause, at least one
neighbor of the clause vertex is in the dominating set, so the clause vertex is
dominated. If the clause is unsatisfied, the clause vertex would need to be
included itself, exceeding the budget ``k = m``. Hence the formula is satisfiable
iff the constructed graph has a dominating set of size at most ``m``.
"""

from __future__ import annotations

from typing import List, Dict, Set, Tuple

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict
        A 3‑SAT instance as defined by :class:`ThreeSat`.

    Returns
    -------
    dict
        A Dominating Set instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """
    # Validate source instance.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex layout:
    #   For each variable i (1‑based) we allocate three vertices:
    #       true  = 3*(i-1)
    #       false = 3*(i-1) + 1
    #       dummy = 3*(i-1) + 2
    #   Clause vertices start after the 3*m variable vertices.
    var_true = lambda i: 3 * (i - 1)
    var_false = lambda i: 3 * (i - 1) + 1
    var_dummy = lambda i: 3 * (i - 1) + 2

    clause_offset = 3 * m
    edges_set: Set[Tuple[int, int]] = set()

    # Add triangle gadget edges for each variable.
    for i in range(1, m + 1):
        t = var_true(i)
        f = var_false(i)
        d = var_dummy(i)
        # Complete triangle (t,f), (t,d), (f,d)
        edges_set.add((min(t, f), max(t, f)))
        edges_set.add((min(t, d), max(t, d)))
        edges_set.add((min(f, d), max(f, d)))

    # Add clause vertices and connect them to the literal vertices that would satisfy the clause.
    for idx, clause in enumerate(clauses):
        c_vertex = clause_offset + idx
        for lit in clause:
            var = abs(lit)
            lit_vertex = var_true(var) if lit > 0 else var_false(var)
            edges_set.add((min(c_vertex, lit_vertex), max(c_vertex, lit_vertex)))

    # Convert edge set to required list format, sorted for determinism.
    edges = [[u, v] for (u, v) in sorted(edges_set)]

    total_vertices = clause_offset + len(clauses)
    k = m  # budget equals number of variables

    result: Dict = {"n": total_vertices, "edges": edges, "k": k}
    DominatingSet.validate(result)
    return result

