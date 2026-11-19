"""Reduction from 3-SAT to Clique.

The reduction follows the classic textbook construction:

* For each clause C_i (i from 0 to q-1) and each literal ℓ in C_i we create a
  vertex v_{i,ℓ}.  Thus the graph has exactly 3·q vertices.
* Two vertices from *different* clauses are connected by an edge iff the two
  corresponding literals are **not** contradictory, i.e. they are not of the
  form x and ¬x for the same variable x.
* The target parameter k is set to the number of clauses q.

It is well‑known that the original formula is satisfiable iff the constructed
graph contains a clique of size q: a satisfying assignment picks exactly one
true literal from each clause, and the chosen literals are pairwise compatible,
+hence the corresponding vertices form a clique.

The implementation below validates the source instance using the provided
``ThreeSat.validate`` method, builds the graph as described, and returns a
dictionary suitable for the ``Clique`` problem.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, Clique


def _literal_key(literal: int) -> Tuple[int, bool]:
    """Return a canonical representation of a literal.

    The representation is a pair ``(var, sign)`` where ``var`` is the variable
    index (positive integer) and ``sign`` is ``True`` for a positive literal
    and ``False`` for a negative literal.
    """
    return (abs(literal), literal > 0)


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Clique`` format such that the answer
        (yes/no) is preserved.
    """
    # Validate the source instance – this will raise InvalidInstance on error.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: no clauses. The formula is trivially satisfiable. We can
    # output an empty graph with k = 0 (k <= 0 is always a yes‑instance).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices. We assign a consecutive integer id to each literal in
    # each clause. The mapping is stored in ``vertex_of[(clause_index, lit)]``.
    vertex_of: Dict[Tuple[int, int], int] = {}
    vertices: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            v_id = len(vertices)
            vertex_of[(ci, lit)] = v_id
            vertices.append((ci, lit))

    n = len(vertices)
    edges: List[List[int]] = []

    # Connect vertices from different clauses if literals are compatible.
    for i in range(n):
        ci, lit_i = vertices[i]
        var_i, sign_i = _literal_key(lit_i)
        for j in range(i + 1, n):
            cj, lit_j = vertices[j]
            if ci == cj:
                # Same clause – we never add edges inside a clause.
                continue
            var_j, sign_j = _literal_key(lit_j)
            # Literals are contradictory iff they refer to the same variable
            # with opposite signs.
            if var_i == var_j and sign_i != sign_j:
                continue
            edges.append([i, j])

    # The target parameter k is the number of clauses.
    k = num_clauses

    # Validate the produced target instance before returning.
    target_instance = {"n": n, "edges": edges, "k": k}
    Clique.validate(target_instance)
    return target_instance

