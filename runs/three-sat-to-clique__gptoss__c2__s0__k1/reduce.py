"""Reduction from 3‑SAT to Clique.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  A literal
is represented by an integer: ``+v`` for the positive literal of variable
``v`` and ``-v`` for its negation.  Every clause contains exactly three
different variables.

The target problem is ``Clique`` with an instance format ``{"n": n,
"edges": [[u, v], ...], "k": k}``.  Vertices are numbered ``0..n‑1`` and the
edge list must contain each undirected edge exactly once (with ``u < v``).

The classic polynomial‑time reduction works as follows:

* For each clause create three vertices – one for each literal in the
  clause.  Vertex ``i`` corresponds to clause ``i // 3`` and literal
  position ``i % 3``.
* Add an edge between two vertices if they belong to **different** clauses
  **and** the corresponding literals are not contradictory (i.e. they are
  not the same variable with opposite signs).  If the literals are the same
  sign or refer to different variables they are compatible.
* Set ``k`` to the number of clauses.  A clique of size ``k`` exactly chooses
  one literal from each clause, and compatibility guarantees that the chosen
  literals can be simultaneously satisfied.

Edge cases:
  * When the formula contains no clauses it is trivially satisfiable.  The
    reduction returns a graph with ``k = 0`` (always a yes‑instance for
    Clique) and no vertices.
  * The reduction does not rely on ``num_vars`` other than for validation –
    the construction works for any ``m``.

The function runs in time polynomial in the size of the 3‑SAT instance
(``O(c^2)`` where ``c`` is the number of clauses) which satisfies the
requirement.
"""

from typing import List, Dict, Any


def _literal_info(lit: int) -> (int, bool):
    """Return the variable index and its sign.

    ``lit`` is encoded as ``+v`` for a positive literal and ``-v`` for a
    negative literal.  The function returns ``(v, is_positive)`` where
    ``is_positive`` is ``True`` for a positive literal.
    """
    if lit > 0:
        return lit, True
    else:
        return -lit, False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": [...], "k": k}`` that is a
        yes‑instance iff the given 3‑SAT instance is satisfiable.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Each clause contributes exactly three vertices.
    n = num_clauses * 3
    edges: List[List[int]] = []

    # Pre‑compute literal information for every vertex.
    # vertex_info[i] = (var, positive)
    vertex_info: List[(int, bool)] = []
    for clause in clauses:
        for lit in clause:
            vertex_info.append(_literal_info(lit))

    # Build edges between compatible vertices from different clauses.
    for i in range(n):
        clause_i = i // 3
        var_i, pos_i = vertex_info[i]
        for j in range(i + 1, n):
            clause_j = j // 3
            if clause_i == clause_j:
                # Vertices from the same clause must not be connected.
                continue
            var_j, pos_j = vertex_info[j]
            # Incompatible if same variable with opposite signs.
            if var_i == var_j and pos_i != pos_j:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": num_clauses}

