"""Reduction from 3‑SAT to Clique.

The source problem is represented as a dictionary with the keys
``"num_vars"`` (the number of variables, an integer) and ``"clauses"`` – a
list of clauses, each clause being a list of three integers.  A literal is
encoded as ``+v`` for the positive literal *v* and ``-v`` for the negated
literal.  The instance conforms to the description in ``problems.py``.

The target problem is the *Clique* problem.  Its instance format is a
dictionary with the keys ``"n"`` (number of vertices), ``"edges"`` – a list
of undirected edges ``[u, v]`` with ``u != v`` – and ``"k"`` (the required
clique size).

The classic polynomial‑time reduction works as follows:

* For each clause create three vertices, one for each literal.
* Connect two vertices belonging to **different** clauses unless the two
  literals are contradictory (i.e. they refer to the same variable with
  opposite signs).  This guarantees that a set containing one vertex from each clause forms a clique exactly when the chosen literals are pairwise non‑contradictory, which corresponds to a satisfying assignment.
* Set ``k`` to the number of clauses.  A clique of size *k* therefore picks
  one vertex from every clause, yielding a satisfying assignment.

Edge cases:
  * An instance with **no clauses** is trivially satisfiable.  We map it to
    a Clique instance with ``k = 0`` (always a yes‑instance) and no vertices.

The implementation below follows this construction while keeping the
runtime polynomial in the size of the 3‑SAT instance.
"""

from typing import List, Dict


def _literal_info(lit: int) -> tuple[int, bool]:
    """Return ``(variable, sign)`` for a literal.

    ``sign`` is ``True`` for a positive literal (``+v``) and ``False`` for a
    negative literal (``-v``).
    """
    return abs(lit), lit > 0


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}`` representing the
        Clique problem.  The returned instance is a yes‑instance iff the
        original 3‑SAT instance is satisfiable.
    """
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: no clauses → always satisfiable.  Use k = 0 which is a
    # guaranteed yes‑instance for Clique.
    if not clauses:
        return {"n": 0, "edges": [], "k": 0}

    num_clauses = len(clauses)
    n = num_clauses * 3  # three vertices per clause
    edges: List[List[int]] = []

    # Build edges between vertices of different clauses when literals are
    # not contradictory.
    for i, clause_i in enumerate(clauses):
        for idx_i, lit_i in enumerate(clause_i):
            var_i, sign_i = _literal_info(lit_i)
            vertex_i = i * 3 + idx_i
            for j in range(i + 1, num_clauses):
                clause_j = clauses[j]
                for idx_j, lit_j in enumerate(clause_j):
                    var_j, sign_j = _literal_info(lit_j)
                    # Skip if literals are contradictory.
                    if var_i == var_j and sign_i != sign_j:
                        continue
                    vertex_j = j * 3 + idx_j
                    # Store edge with smaller index first for consistency.
                    if vertex_i < vertex_j:
                        edges.append([vertex_i, vertex_j])
                    else:
                        edges.append([vertex_j, vertex_i])

    k = num_clauses
    return {"n": n, "edges": edges, "k": k}

