"""Reduction from SAT to Independent Set.

The source problem is SAT in conjunctive normal form.  An instance is a
dictionary with the keys:

    * ``num_vars`` – the number of variables (variables are numbered 1..m)
    * ``clauses`` – a list of clauses, each clause being a list of literals.

A literal is represented as a string ``"+v"`` meaning *v* is true or
``"-v"`` meaning *v* is false (where ``v`` is an integer variable index).  The
definition matches the doc‑string in ``problems.py``.

The target problem is Independent Set.  Its instance format is a dictionary
with the keys:

    * ``n`` – number of vertices (vertices are 0..n‑1)
    * ``edges`` – list of undirected edges, each edge a two‑element list
      ``[u, v]`` with ``u != v``.  Each edge appears only once, order does not
      matter.
    * ``k`` – the required size of the independent set (we ask for at least
      ``k`` vertices).

We implement the classic polynomial‑time many‑one reduction:

    * For every literal occurrence in a clause we create a distinct vertex.
    * All vertices belonging to the same clause are made pairwise adjacent –
      this forces any independent set to contain **at most one** vertex from
      each clause.
    * Vertices that correspond to complementary literals (``+v`` and ``-v``)
      are also made adjacent, even if they belong to different clauses.  This
      guarantees that an independent set cannot pick both a variable and its
      negation.
    * We set ``k`` equal to the number of clauses.  An independent set of size
      ``k`` therefore picks exactly one literal from each clause, and the
      complement‑edge condition ensures that the chosen literals are
      consistent, i.e., they define a satisfying assignment.

Edge cases handled explicitly:

    * **No clauses** – the SAT instance is trivially satisfiable.  We return a
      graph with ``k = 0`` (always a yes‑instance of Independent Set).
    * **Empty clause** – such a clause can never be satisfied, so the SAT
      instance is a no‑instance.  We construct a graph where ``k > n`` (e.g.,
      ``n = 0, k = 1``), which Independent Set also rejects.

The reduction runs in polynomial time with respect to the size of the SAT
instance (the number of literal occurrences).  The implementation avoids
duplicating edges by storing them in a ``set`` of ordered tuples.
"""

from typing import Dict, List, Tuple, Set


def _parse_literal(lit: str) -> Tuple[int, bool]:
    """Return (variable_index, is_positive) for a literal string.

    The SAT format uses ``"+v"`` for a positive literal and ``"-v"`` for a
    negative literal where ``v`` is a decimal integer.
    """
    if not lit:
        raise ValueError("Empty literal string")
    sign = lit[0]
    if sign not in {"+", "-"}:
        raise ValueError(f"Invalid literal sign: {lit}")
    var = int(lit[1:])
    return var, sign == "+"


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance matching the format described in the problem
        definition.

    Returns
    -------
    dict
        An Independent Set instance where the answer is *yes* iff the SAT
        instance is satisfiable.
    """
    clauses: List[List[str]] = instance.get("clauses", [])

    # Edge case: formula with no clauses is always satisfiable.
    if len(clauses) == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Edge case: any empty clause makes the formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            # Create a graph where k > n to guarantee a NO answer.
            return {"n": 0, "edges": [], "k": 1}

    # Normal case.
    vertex_id = 0
    clause_vertices: List[List[int]] = []  # vertices belonging to each clause
    literal_info: List[Tuple[int, bool]] = []  # index by vertex id -> (var, pos)

    for clause in clauses:
        current: List[int] = []
        for lit in clause:
            # Create a vertex for each literal occurrence.
            current.append(vertex_id)
            literal_info.append(_parse_literal(lit))
            vertex_id += 1
        clause_vertices.append(current)

    n = vertex_id
    edges_set: Set[Tuple[int, int]] = set()

    # 1. Add edges inside each clause (make the clause a clique).
    for verts in clause_vertices:
        sz = len(verts)
        for i in range(sz):
            for j in range(i + 1, sz):
                u, v = verts[i], verts[j]
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # 2. Add edges between complementary literals across different clauses.
    #    We compare every pair of vertices from different clauses.
    #    Since the graph can be large, we use a dictionary mapping (var, sign)
    #    to the list of vertices that represent that literal.  Then we connect
    #    each vertex with all vertices of the opposite sign for the same var.
    pos_map: Dict[int, List[int]] = {}
    neg_map: Dict[int, List[int]] = {}
    for vid, (var, is_pos) in enumerate(literal_info):
        (pos_map if is_pos else neg_map).setdefault(var, []).append(vid)

    for var in set(pos_map.keys()).intersection(neg_map.keys()):
        for u in pos_map[var]:
            for v in neg_map[var]:
                a, b = (u, v) if u < v else (v, u)
                edges_set.add((a, b))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in edges_set]

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

