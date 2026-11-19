"""Polynomial-time reduction from SAT to Independent Set.

The source problem is defined in ``problems.Sat`` and the target problem
in ``problems.IndependentSet``.  Both classes only provide a ``validate``
method – they do **not** contain solvers.  The reduction must therefore be
implemented purely by constructing a graph that respects the classic
Karp reduction:

* For each clause we create a *clique* – one vertex for every literal in
  the clause.  Selecting at most one vertex from each clique guarantees
  that we pick at most one literal per clause.
* Vertices belonging to different clauses are connected exactly when the
  corresponding literals are *complementary* (e.g. ``+x`` and ``-x``).  An
  independent set cannot contain contradictory literals.
* The parameter ``k`` of the Independent‑Set instance is set to the number
  of clauses.  An independent set of size ``k`` therefore picks one vertex
  from each clause, yielding a satisfying assignment for the original SAT
  formula.

Edge‑case handling mirrors the specifications in ``problems.py``:

* If the SAT instance has **no clauses**, it is trivially satisfiable.  We
  return an empty graph (``n = 0``) with ``k = 0`` – a yes‑instance for the
  Independent‑Set problem because ``k <= 0`` is always true.
* If a clause is empty, the SAT instance is unsatisfiable.  The reduction
  creates a graph that has fewer vertices than ``k`` (zero vertices for the
  empty clause), making a size‑``k`` independent set impossible.

The implementation runs in polynomial time in the size of the SAT
instance.  All edges are stored only once (``u < v``) to satisfy the
validation rules of the target problem.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List

from problems import Sat, IndependentSet


def _complement(lit1: int, lit2: int) -> bool:
    """Return ``True`` iff ``lit1`` and ``lit2`` are complementary literals.

    Two literals are complementary when they refer to the same variable
    with opposite signs, i.e. ``lit1 == -lit2``.
    """

    return lit1 == -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Sat`` specification:
        ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.

    Returns
    -------
    dict
        A dictionary adhering to the ``IndependentSet`` specification:
        ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """

    # Validate the source instance.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # No clauses -> trivially satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal occurrence.
    clause_vids: List[List[int]] = []          # clause index -> list of vertex ids
    lit_of_vid: Dict[int, int] = {}           # vertex id -> literal value
    current_id = 0
    for clause in clauses:
        vids_this: List[int] = []
        for lit in clause:
            vid = current_id
            current_id += 1
            vids_this.append(vid)
            lit_of_vid[vid] = lit
        clause_vids.append(vids_this)

    n = current_id
    edges_set = set()

    # 1. Make each clause a clique.
    for vids in clause_vids:
        for u, v in combinations(vids, 2):
            if u > v:
                u, v = v, u
            edges_set.add((u, v))

    # 2. Connect complementary literals from different clauses.
    for i, vids_i in enumerate(clause_vids):
        for j in range(i + 1, len(clause_vids)):
            vids_j = clause_vids[j]
            for v1 in vids_i:
                for v2 in vids_j:
                    if _complement(lit_of_vid[v1], lit_of_vid[v2]):
                        u, v = (v1, v2) if v1 < v2 else (v2, v1)
                        edges_set.add((u, v))

    edges = [[u, v] for u, v in sorted(edges_set)]
    k = num_clauses

    result = {"n": n, "edges": edges, "k": k}
    IndependentSet.validate(result)
    return result

