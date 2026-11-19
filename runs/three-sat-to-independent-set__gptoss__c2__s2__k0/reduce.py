"""Reduction from 3‑SAT to Independent Set.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable *v* is true) or
``-v`` (variable *v* is false).  Every clause contains exactly three
different variables.

The target problem is ``IndependentSet`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction is the classic one used in textbooks:

* For each clause we create a triangle (three vertices, all pairwise
  adjacent).  Selecting at most one vertex from each triangle guarantees
  that the independent set can contain at most one literal per clause.
* For any two vertices that correspond to complementary literals
  (``+x`` and ``-x``) we add an edge between them.  This prevents the
  independent set from choosing both a variable and its negation.
* We ask for an independent set of size ``k`` where ``k`` equals the
  number of clauses.  An independent set of that size picks exactly one
  vertex from each triangle, which yields a satisfying assignment for
  the original formula, and vice‑versa.

The implementation follows this description and runs in polynomial time
with respect to the size of the 3‑SAT instance.
"""

from typing import List, Dict, Any, Tuple, Set


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as
        described in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses – the formula is trivially satisfiable.
    # We return an empty graph with k = 0, which is always a YES‑instance.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # ------------------------------------------------------------------
    # Build vertices.  One vertex per literal occurrence (i.e., per entry
    # in each clause).  Vertex IDs are 0‑based and assigned consecutively.
    # ------------------------------------------------------------------
    vertex_info: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n = len(vertex_info)  # total vertices = 3 * num_clauses

    # ------------------------------------------------------------------
    # Helper to add an undirected edge to the set, ensuring the smaller
    # endpoint comes first.  Using a set removes duplicates automatically.
    # ------------------------------------------------------------------
    edges: Set[Tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        edges.add((u, v) if u < v else (v, u))

    # ------------------------------------------------------------------
    # 1. Connect vertices inside each clause to form a triangle.
    # ------------------------------------------------------------------
    start = 0
    for clause in clauses:
        ids = list(range(start, start + 3))
        # add the three edges of the triangle
        add_edge(ids[0], ids[1])
        add_edge(ids[0], ids[2])
        add_edge(ids[1], ids[2])
        start += 3

    # ------------------------------------------------------------------
    # 2. Connect complementary literals across different clauses.
    #    For each variable we connect every positive occurrence with every
    #    negative occurrence.
    # ------------------------------------------------------------------
    lit_to_vertices: Dict[int, List[int]] = {}
    for vid, (_, lit) in enumerate(vertex_info):
        lit_to_vertices.setdefault(lit, []).append(vid)

    for lit, pos_vertices in lit_to_vertices.items():
        if lit > 0:
            neg_vertices = lit_to_vertices.get(-lit, [])
            for u in pos_vertices:
                for v in neg_vertices:
                    add_edge(u, v)

    # Convert edge set to the required list format.
    edge_list: List[List[int]] = [list(e) for e in edges]

    return {"n": n, "edges": edge_list, "k": num_clauses}

