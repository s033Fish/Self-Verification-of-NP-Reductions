"""Reduction from SAT (CNF satisfiability) to Independent Set.

The reduction follows the classic construction:

* For each clause C_i we create a vertex for every literal that appears
  in the clause. Vertices belonging to the same clause form a *clique*
  (every pair is connected).  This forces an independent set to contain at
  most one vertex from each clause.
* For any two vertices that correspond to complementary literals (e.g.
  x and -x) we also add an edge.  This prevents the independent set from
  picking contradictory assignments.
* The target parameter ``k`` is set to the number of clauses.  An
  independent set of size ``k`` therefore selects exactly one literal from
  each clause, and the selections are pairwise non‑conflicting – which is
  precisely a satisfying assignment for the original formula.

Edge‑case handling mirrors the specification in ``problems.py``:

* **No clauses** – the formula is trivially satisfiable.  We output a graph
  with ``n = 0`` vertices, no edges and ``k = 0``.  ``k <= 0`` is always a
  yes‑instance for Independent Set.
* **Empty clause** – such a clause can never be satisfied, so the SAT
  instance is a no‑instance.  We produce a graph where ``k > n`` (e.g.
  ``n = 0`` and ``k = 1``), which is also a no‑instance for Independent Set.

The implementation runs in time polynomial in the size of the SAT
instance (linear in the number of literals plus the number of complementary
pairs), which satisfies the required complexity bound.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Set

from problems import Sat, IndependentSet

def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format described by ``Sat``.

    Returns
    -------
    dict
        An instance of ``IndependentSet`` such that the answer to the
        Independent Set instance is *yes* iff the original SAT instance is
        *yes*.
    """
    # Validate the input according to the SAT specification.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(clause) == 0 for clause in clauses):
        # Return a trivially unsatisfiable Independent Set instance.
        return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses – always satisfiable.
    if len(clauses) == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for each literal in each clause.
    # We keep a parallel list mapping vertex id -> (var, sign).
    vertex_literal: List[Tuple[int, int]] = []  # (var, sign) where sign is +1 or -1
    clause_vertices: List[List[int]] = []  # list of vertex ids per clause
    for clause in clauses:
        cur: List[int] = []
        for lit in clause:
            var = abs(lit)
            sign = 1 if lit > 0 else -1
            vertex_id = len(vertex_literal)
            vertex_literal.append((var, sign))
            cur.append(vertex_id)
        clause_vertices.append(cur)

    n = len(vertex_literal)
    edges_set: Set[frozenset[int]] = set()

    # 1. Add edges inside each clause to form a clique.
    for verts in clause_vertices:
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                edges_set.add(frozenset((verts[i], verts[j])))

    # 2. Add edges between complementary literals across the whole graph.
    #    Two vertices are complementary if they refer to the same variable
    #    with opposite signs.
    # Build a map from (var, sign) to vertex ids for quick lookup.
    var_to_pos: Dict[int, List[int]] = {}
    var_to_neg: Dict[int, List[int]] = {}
    for vid, (var, sign) in enumerate(vertex_literal):
        if sign == 1:
            var_to_pos.setdefault(var, []).append(vid)
        else:
            var_to_neg.setdefault(var, []).append(vid)

    for var in range(1, num_vars + 1):
        pos_list = var_to_pos.get(var, [])
        neg_list = var_to_neg.get(var, [])
        for p in pos_list:
            for q in neg_list:
                edges_set.add(frozenset((p, q)))

    # Convert edge set to the required list format.
    edges = [[u, v] for edge in edges_set for u, v in (tuple(edge),)]

    k = len(clauses)
    result = {"n": n, "edges": edges, "k": k}
    # Validate the produced instance according to IndependentSet.
    IndependentSet.validate(result)
    return result

