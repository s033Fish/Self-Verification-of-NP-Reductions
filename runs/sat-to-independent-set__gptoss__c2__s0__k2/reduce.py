"""Reduction from SAT (CNF) to Independent Set.

The source problem (SAT) is defined as:
    instance = {"num_vars": m, "clauses": [[literal, ...], ...]}
    literals are integers where a positive value +v means variable v is true
    and a negative value -v means variable v is false.

The target problem (Independent Set) expects:
    instance = {"n": n, "edges": [[u, v], ...], "k": k}
    vertices are 0..n-1 and edges are undirected pairs.

We implement the classic polynomial‑time reduction:
    * For each clause we create a vertex for every literal occurring in that
      clause.
    * All vertices belonging to the same clause are made adjacent (a clique).
      This forces an independent set to pick at most one literal from each clause.
    * Vertices representing complementary literals of the same variable are
      also connected.  This prevents the independent set from selecting both a
      variable and its negation.
    * We ask for an independent set of size k equal to the number of clauses.

Correctness:
    * If the formula is satisfiable, choose for each clause a literal that is
      true under a satisfying assignment. Those vertices are pairwise
      non‑adjacent, giving an independent set of size k.
    * Conversely, an independent set of size k must contain exactly one vertex
      from each clause (because of the intra‑clause cliques) and cannot contain
      complementary literals, which yields a consistent truth assignment that
      satisfies every clause.

Edge‑case handling:
    * No clauses → the formula is trivially satisfiable. We return a trivial
      Independent‑Set instance with k=0 (always a yes‑instance).
    * Presence of an empty clause → the formula is unsatisfiable. We return a
      graph with n=0 and k=1; since k>n the Independent‑Set instance is a
      definite no‑instance.

The implementation runs in polynomial time in the size of the SAT instance.
"""

from __future__ import annotations

import itertools
from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        SAT instance with keys "num_vars" and "clauses" as described above.

    Returns
    -------
    dict
        Independent Set instance with keys "n", "edges", and "k".
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # ---- Edge cases -----------------------------------------------------
    # Empty clause -> unsatisfiable
    for clause in clauses:
        if len(clause) == 0:
            # No vertices, but request k=1 > n, guaranteeing a NO answer.
            return {"n": 0, "edges": [], "k": 1}

    # No clauses -> trivially satisfiable
    if len(clauses) == 0:
        # k=0 is always YES.
        return {"n": 0, "edges": [], "k": 0}

    # ---- Build vertices -------------------------------------------------
    # vertex_info maps vertex id -> (clause_index, literal)
    vertex_info: List[Tuple[int, int]] = []
    clause_vertices: List[List[int]] = []  # list of vertex ids per clause

    for ci, clause in enumerate(clauses):
        ids: List[int] = []
        for lit in clause:
            vid = len(vertex_info)
            vertex_info.append((ci, lit))
            ids.append(vid)
        clause_vertices.append(ids)

    n = len(vertex_info)
    edges_set = set()

    # ---- Intra‑clause edges (make each clause a clique) -----------------
    for ids in clause_vertices:
        for u, v in itertools.combinations(ids, 2):
            if u > v:
                u, v = v, u
            edges_set.add((u, v))

    # ---- Complementary literal edges across clauses ----------------------
    # Group vertices by variable and sign.
    pos: Dict[int, List[int]] = {}
    neg: Dict[int, List[int]] = {}
    for vid, (_, lit) in enumerate(vertex_info):
        var = abs(lit)
        if lit > 0:
            pos.setdefault(var, []).append(vid)
        else:
            neg.setdefault(var, []).append(vid)

    for var in range(1, m + 1):
        for u in pos.get(var, []):
            for v in neg.get(var, []):
                # Ensure ordering for the set
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    edges = [list(e) for e in edges_set]
    k = len(clauses)

    return {"n": n, "edges": edges, "k": k}

