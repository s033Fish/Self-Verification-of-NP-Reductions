"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem format (see problems.py) is a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where each literal is an integer: positive ``v`` means variable ``v`` is
True, negative ``-v`` means variable ``v`` is False.

The target problem (Clique) expects a dictionary:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n‑1 and ``edges`` contains each undirected
edge exactly once (order of the two endpoints does not matter).

Standard polynomial‑time reduction:
    * For each clause *i* and each literal ℓ in that clause create a vertex
      representing the *occurrence* (i, ℓ).
    * Connect two vertices from different clauses iff the corresponding
      literals are *compatible* – i.e., they are not contradictory
      (they do not refer to the same variable with opposite signs).
    * Set ``k`` to the number of clauses.

Correctness:
    * A k‑clique corresponds to picking one literal from each clause such
      that the chosen literals are pairwise compatible, which exactly
      describes a satisfying assignment.
    * Edge cases are handled automatically:
        - If there are no clauses, ``k = 0`` and the Clique instance is a
          trivial yes‑instance.
        - If any clause is empty, there will be no vertex for that clause,
          so the maximum clique size is at most ``c-1`` where ``c`` is the
          total number of clauses; hence the answer is no.

The implementation follows this construction and runs in O(V^2) time,
which is polynomial in the size of the SAT instance.
"""

from typing import List, Dict, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        SAT instance with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        Clique instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Mapping from (clause_index, literal) to vertex id
    vertex_id = 0
    clause_literal_to_vid: List[List[Tuple[int, int]]] = []  # per clause list of (lit, vid)
    for ci, clause in enumerate(clauses):
        lits_vids: List[Tuple[int, int]] = []
        for lit in clause:
            lits_vids.append((lit, vertex_id))
            vertex_id += 1
        clause_literal_to_vid.append(lits_vids)

    n = vertex_id  # total number of vertices
    edges: List[List[int]] = []

    def compatible(l1: int, l2: int) -> bool:
        """Return True iff the two literals can appear together.
        They are incompatible only when they are exact opposites (e.g., 5 and -5).
        """
        return l1 != -l2

    # Add edges between vertices from different clauses when compatible
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for lit_i, vid_i in clause_literal_to_vid[i]:
                for lit_j, vid_j in clause_literal_to_vid[j]:
                    if compatible(lit_i, lit_j):
                        if vid_i < vid_j:
                            edges.append([vid_i, vid_j])
                        else:
                            edges.append([vid_j, vid_i])

    k = num_clauses
    return {"n": n, "edges": edges, "k": k}

