"""Reduction from SAT to Clique.

The source problem is SAT (CNF satisfiability) with instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Literals are represented as signed integers: ``+v`` means the variable ``v``
should be true, ``-v`` means it should be false.  Clauses are lists of such
integers; an empty clause is unsatisfiable, while a formula with no clauses is
trivially satisfiable.

The target problem is Clique with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction follows the classic textbook construction:

* For every literal occurrence in every clause we create a vertex.
* Vertices belonging to the same clause are never connected.
* Vertices from different clauses are connected **iff** the corresponding
  literals are *compatible*, i.e. they do not contradict each other.  Two
  literals contradict each other only when they involve the same variable with
  opposite signs (e.g. ``+3`` and ``-3``).
* We ask for a clique of size ``k = number_of_clauses``.  Such a clique selects
  exactly one literal from each clause, and the compatibility condition ensures
  that the selected literals can be simultaneously satisfied.

Edge‑cases are handled explicitly:

* If the SAT instance has **no clauses**, it is always satisfiable.  We return a
  Clique instance with ``k = 0`` (always a yes‑instance).
* If any clause is **empty**, the SAT instance is unsatisfiable.  We return a
  Clique instance where ``k > n`` (e.g. ``n = 0, k = 1``) which is always a
  no‑instance.

The implementation runs in polynomial time with respect to the size of the
input (the number of literals).  No external solvers are invoked.
"""

from typing import Dict, List, Tuple


def _parse_literal(lit: int) -> Tuple[int, bool]:
    """Return (variable, is_positive) for a literal.

    ``lit`` is an integer where the sign encodes polarity.  ``+v`` (or ``v``)
    means the variable ``v`` should be true, ``-v`` means it should be false.
    """
    if lit > 0:
        return lit, True
    else:
        return -lit, False


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary matching the SAT format described above.

    Returns
    -------
    dict
        A dictionary matching the Clique format.  The returned instance is a
        yes‑instance iff the original SAT instance is satisfiable.
    """
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: formula with no clauses is trivially satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Edge case: any empty clause makes the formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            # Return a Clique instance where k > n to guarantee a NO answer.
            return {"n": 0, "edges": [], "k": 1}

    # Create a vertex for each literal occurrence.
    # Mapping from (clause_index, literal_index) -> vertex id.
    vertex_id = 0
    vertex_info: List[Tuple[int, bool]] = []  # stores parsed literal for each vertex id
    clause_vertex_ids: List[List[int]] = []   # list of vertex ids per clause
    for ci, clause in enumerate(clauses):
        ids_this_clause: List[int] = []
        for lit in clause:
            vertex_info.append(_parse_literal(lit))
            ids_this_clause.append(vertex_id)
            vertex_id += 1
        clause_vertex_ids.append(ids_this_clause)

    n = vertex_id
    edges: List[List[int]] = []

    # Add edges between vertices of different clauses when compatible.
    for ci in range(num_clauses):
        for cj in range(ci + 1, num_clauses):
            for vi in clause_vertex_ids[ci]:
                var_i, pos_i = vertex_info[vi]
                for vj in clause_vertex_ids[cj]:
                    var_j, pos_j = vertex_info[vj]
                    # Incompatible only if same variable with opposite polarity.
                    if var_i == var_j and pos_i != pos_j:
                        continue
                    edges.append([vi, vj])

    return {"n": n, "edges": edges, "k": num_clauses}

