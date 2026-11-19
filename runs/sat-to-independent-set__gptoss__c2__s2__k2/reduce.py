"""Reduction from SAT to Independent Set.

The source problem is SAT in CNF as described in ``problems.py``:

    {
        "num_vars": m,
        "clauses": [[literal, ...], ...]
    }

where a literal is an integer ``+v`` (variable ``v`` is true) or ``-v``
(variable ``v`` is false).  A clause is a list of literals and may be
empty.

The target problem is Independent Set with instance format:

    {
        "n": n,                # number of vertices (0‑based indices)
        "edges": [[u, v], ...],# undirected edges, no duplicates
        "k": k                 # size threshold
    }

The classic polynomial‑time reduction creates a vertex for every literal
occurrence.  Vertices belonging to the same clause form a clique – this
forces an independent set to pick **at most** one literal from each
clause.  Additionally, vertices representing complementary literals
(``+v`` and ``-v``) are connected, ensuring the independent set cannot
contain both a variable and its negation.  Setting ``k`` to the number
of clauses yields the equivalence:

*An independent set of size ≥ k exists ⇔ the SAT formula is satisfiable.*

Edge cases are handled automatically:
    * No clauses → k = 0, n = 0, graph empty → always yes.
    * Empty clause → the clause contributes 0 vertices, so n < k → no.

The implementation runs in polynomial time with respect to the size of
the SAT instance.
"""

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance with keys ``"num_vars"`` and ``"clauses"`` as
        described in the module docstring.

    Returns
    -------
    dict
        An Independent Set instance with keys ``"n"``, ``"edges"`` and
        ``"k"``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Mapping from (clause_index, position_in_clause) -> vertex id
    vertex_id = 0
    clause_vertices: List[List[int]] = []  # list per clause of vertex ids
    # Store literal information for each vertex id
    literal_of: List[Tuple[int, int]] = []  # (var, sign) where sign = +1 or -1

    for ci, clause in enumerate(clauses):
        cur_ids: List[int] = []
        for lit in clause:
            cur_ids.append(vertex_id)
            var = abs(lit)
            sign = 1 if lit > 0 else -1
            literal_of.append((var, sign))
            vertex_id += 1
        clause_vertices.append(cur_ids)

    n = vertex_id  # total number of vertices
    edges_set = set()

    # 1. Add edges to make each clause a clique
    for cur_ids in clause_vertices:
        l = len(cur_ids)
        for i in range(l):
            for j in range(i + 1, l):
                u, v = cur_ids[i], cur_ids[j]
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # 2. Add edges between complementary literals across all vertices
    # Build a map from (var, sign) to list of vertex ids
    var_sign_to_vertices: Dict[Tuple[int, int], List[int]] = {}
    for vid, (var, sign) in enumerate(literal_of):
        var_sign_to_vertices.setdefault((var, sign), []).append(vid)

    for var in range(1, instance.get("num_vars", 0) + 1):
        pos_vertices = var_sign_to_vertices.get((var, 1), [])
        neg_vertices = var_sign_to_vertices.get((var, -1), [])
        for u in pos_vertices:
            for v in neg_vertices:
                a, b = (u, v) if u < v else (v, u)
                edges_set.add((a, b))

    # Convert edge set to required list format
    edges = [[u, v] for (u, v) in edges_set]

    return {"n": n, "edges": edges, "k": num_clauses}

