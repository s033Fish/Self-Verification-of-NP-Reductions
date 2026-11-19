"""Reduction from 3‑SAT to Dominating Set.

The source problem is represented by a dictionary with the keys
``"num_vars"`` (the number of variables *m*) and ``"clauses"`` – a list of
clauses, each clause being a list of three literals.  A literal is an
integer of the form ``+v`` (meaning variable *v* is true) or ``-v`` (meaning
variable *v* is false).  The specification of the source problem is given
in ``problems.py`` and reproduced in the task description.

The target problem is Dominating Set.  An instance is a dictionary with the
keys ``"n"`` (number of vertices), ``"edges"`` (list of undirected edges as
``[u, v]`` where ``u < v``) and ``"k"`` (the size bound for the dominating
set).  The reduction must produce a graph that has a dominating set of size
``k`` iff the original 3‑SAT instance is satisfiable.

Standard textbook reduction:

* **Variable gadget** – for each variable *x_i* we create three vertices
  ``v_i_T``, ``v_i_F`` and ``d_i`` forming a triangle.  Selecting either
  ``v_i_T`` or ``v_i_F`` (or ``d_i``) dominates the whole gadget.  In a
  satisfying assignment we will choose the vertex corresponding to the
  truth value of the variable.

* **Clause gadget** – for each clause we create three vertices that form a
  triangle.  Each of those three vertices is additionally connected to the
  literal vertex that appears in the clause (the ``v_i_T`` or ``v_i_F``
  from the appropriate variable gadget).

If a clause contains a true literal, then the clause‑triangle is already
 dominated by the selected literal vertex, otherwise we must pick at least
 one vertex from the clause‑triangle.  Consequently the graph has a
 dominating set of size ``m + |C|`` (where ``|C|`` is the number of clauses)
 iff the formula is satisfiable.

The implementation below follows this construction.  Vertices are numbered
sequentially:

* For variable *i* (0‑based) we assign IDs ``3*i``, ``3*i+1`` and ``3*i+2``
  to the true, false and dummy vertices respectively.
* Clause vertices start after the variable vertices.  For clause *j* and
  literal position *p`` (0,1,2) the vertex id is ``3*m + 3*j + p``.

The returned instance respects the format required by ``DominatingSet`` –
edges are undirected, each appears exactly once with the smaller endpoint
first, and ``k`` is set to ``m + len(clauses)``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def _add_edge(edges: Set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge to the set, storing it with ``u < v``.

    The ``edges`` collection is a ``set`` of ``(u, v)`` tuples.  Using a set
    automatically eliminates duplicates that could arise from the
    construction.
    """
    if u == v:
        return
    if u > v:
        u, v = v, u
    edges.add((u, v))


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary with the keys ``"num_vars"`` and ``"clauses"`` as
        described in the problem statement.

    Returns
    -------
    dict
        An instance of the ``DominatingSet`` problem.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Number of vertices contributed by variable gadgets.
    var_vertices = 3 * m
    # Number of vertices contributed by clause gadgets (3 per clause).
    clause_vertices = 3 * len(clauses)
    n = var_vertices + clause_vertices

    edges_set: Set[Tuple[int, int]] = set()

    # ----- Variable gadgets -----
    for i in range(m):
        true_id = 3 * i
        false_id = 3 * i + 1
        dummy_id = 3 * i + 2
        # Form a triangle.
        _add_edge(edges_set, true_id, false_id)
        _add_edge(edges_set, true_id, dummy_id)
        _add_edge(edges_set, false_id, dummy_id)

    # ----- Clause gadgets -----
    base_clause = var_vertices  # first id for clause vertices
    for j, clause in enumerate(clauses):
        # clause is a list of three literals, e.g. [+1, -3, +2]
        if len(clause) != 3:
            # According to the specification this should never happen,
            # but we handle it gracefully.
            raise ValueError("Each clause must contain exactly three literals.")

        # IDs for the three clause vertices.
        c_ids = [base_clause + 3 * j + p for p in range(3)]

        # Connect the three clause vertices to form a triangle.
        _add_edge(edges_set, c_ids[0], c_ids[1])
        _add_edge(edges_set, c_ids[0], c_ids[2])
        _add_edge(edges_set, c_ids[1], c_ids[2])

        # Connect each clause vertex to the corresponding literal vertex.
        for p, lit in enumerate(clause):
            var = abs(lit) - 1  # variables are 1‑based in the input
            if var < 0 or var >= m:
                raise ValueError("Literal refers to a non‑existent variable.")
            # Determine which vertex (true or false) the literal corresponds to.
            if lit > 0:
                literal_vertex = 3 * var  # true vertex
            else:
                literal_vertex = 3 * var + 1  # false vertex
            _add_edge(edges_set, c_ids[p], literal_vertex)

    # Convert edge set to list of lists with u < v as required.
    edges: List[List[int]] = [[u, v] for (u, v) in edges_set]

    # The bound k is m (one vertex per variable gadget) plus the number of
    # clauses.  This matches the classic reduction.
    k = m + len(clauses)

    return {"n": n, "edges": edges, "k": k}

